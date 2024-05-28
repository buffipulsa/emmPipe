
import maya.api.OpenMaya as om
import maya.cmds as cmds

from dev.utils import convert_list_to_str, convert_str_to_list

from rig.objects.object_data import MetaNode, DagNodeData, DependencyNodeData, RebuildObject
from rig.objects.object_utils import transfer_connections
from rig.objects.base_object import BaseObject
from rig.joints.joints import Joints
from rig.controls.control import Control

class SkeletonBase(BaseObject):

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __init__(self):
        super().__init__('SKELETON', 'c', 'base', 0)

        self._joints_grp = None
        self._joints_utils = None
        self._modules_grp = None
        self._controls_grp = None

        self._root_joint = None
        self._root_ctrl = None

    #... Pulbic Methods ...#
    def create(self):
        """
        Creates the osseous base module.

        If the base modules metadata already exists, it rebuilds the base module using the existing metadata.
        Otherwise, it creates a new base module.

        Returns:
            The created base module.
        """
        self._create_module_structure()
        self._create_root_joint()
        self._create_root_control()

        super().create()

        return self
    
    #... Private Methods ...#
    def _create_module_structure(self):

        self._main_grp = self._add_module(self._combined_name, vis_switch=False)

        self._joints_grp = self._add_module('joints', self._main_grp, True)
        self._joints_utils = self._add_module('joints_utils', self._main_grp, True)
        self._modules_grp = self._add_module('modules', self._main_grp, True)            
        self._controls_grp = self._add_module('controls', self._main_grp, True)

        cmds.setAttr(f'{self._joints_grp.dag_path}.overrideEnabled', True)
        cmds.setAttr(f'{self._joints_grp.dag_path}.overrideDisplayType', 2)

    def _create_root_joint(self):
        """
        Creates the root joint for the SkeletonBase rig element.
        """
        self._root_joint = Joints('root', 'c', 1).create()
        cmds.parent(self._root_joint.joints[0].dag_path, self._joints_grp.dag_path)

        self._root_joint.radius = 0.1

        return

    def _create_root_control(self):
        """
        Creates the root control for the SkeletonBase rig element.
        """
        self._root_ctrl = Control('root', 'c', 'main', 0, 'circle').create()
        
        cmds.parent(self._root_ctrl.offset.dag_path, self.controls_grp.dag_path)
        cmds.parent(cmds.parentConstraint(self._root_ctrl.control.dag_path, 
                                          self._root_joint.joints[0].dag_path, mo=True), 
                    self._joints_utils.dag_path)

        return

    def _create_meta_data(self):
        super()._create_meta_data()

        self.data['joints_grp'] = self._joints_grp.dag_path
        self.data['joints_utils'] = self._joints_utils.dag_path
        self.data['modules_grp'] = self._modules_grp.dag_path
        self.data['controls_grp'] = self._controls_grp.dag_path
        self.data['root_joint'] = self._root_joint.joints[0].dag_path
        self.data['root_ctrl'] = self._root_ctrl.control.dag_path

        return self.data
    
    #... Properties ...#
    @property
    def joints_grp(self):
        return self._joints_grp
    
    @joints_grp.setter
    def joints_grp(self, value):
        self._joints_grp = value

    @property
    def joints_utils(self):
        return self._joints_utils
    
    @joints_utils.setter
    def joints_utils(self, value):
        self._joints_utils = value

    @property
    def modules_grp(self):
        return self._modules_grp
    
    @modules_grp.setter
    def modules_grp(self, value):
        self._modules_grp = value
    
    @property
    def controls_grp(self):
        return self._controls_grp
    
    @controls_grp.setter
    def controls_grp(self, value):
        self._controls_grp = value

    @property
    def root_joint(self):
        return self._root_joint

    @root_joint.setter
    def root_joint(self, value):
        self._root_joint = value

    @property
    def root_ctrl(self):
        return self._root_ctrl

    @root_ctrl.setter
    def root_ctrl(self, value):
        self._root_ctrl = value


class SkeletonCreator(BaseObject):

    def __repr__(self):
        return f'{self.__class__.__name__}({self._name!r}, {self._side!r}, {self._desc!r}, {self._index!r}, {self._num_joints!r}, {self._parent!r}, {self._up_type!r})'

    def __init__(self, name, side, desc, index=0, num_joints=1, parent=None, up_type='object', hook_idx=0, replace_hook=False):
        super().__init__(name, side, desc, index)

        self._num_joints = num_joints
        self._parent = self._set_parent(parent)
        self._up_type = up_type.lower() if up_type else None
        self._hook_idx = hook_idx
        self._replace_hook = replace_hook

        self._joints = []
        self._aim_joints = []
        self._aim_vectors = []
        self._aim_offsets = []

        self._ctrls = []

        self._parent_pos = [0, 0, 0]
        self._previous_vec = None

        #print(self._combined_name)

    #... Public Methods ...#
    def create(self):

        self._create_module_structure()

        self._create_joints()
        self._parent_joints()
        self._space_joints()
        self._create_aim_joints()

        self._create_controls()
        self._create_up_ctrl()

        # if self._combined_name == 'arm_l_skeleton_000':
        #     return self

        if self._up_type:
            if self._up_type == 'object':
                self._create_object_aim_setup()
            if self._up_type == 'vector_plane':
                self._create_vector_plane_aim_setup()

        if self._replace_hook:
            self._set_replace_hook()

        super().create()

        return self
    
    #... Private Methods ...#
    def _set_parent(self, parent):
        """
        Checks if the given parent is a valid Osseous instance.

        Args:
            parent (Osseous): The parent object to be checked.

        Returns:
            bool: True if the parent is valid, False otherwise.

        Raises:
            TypeError: If the parent is not an instance of Osseous.
        """
        if parent:
            parent_instance = RebuildObject(f'{parent}_metaData').rebuild()
        else:
            parent_instance = None

        return parent_instance
    
    def _create_module_structure(self):
        """
        Creates the module structure for the osseous rig.
        """
        if not cmds.objExists('skeleton_c_base_000'):
            raise ValueError('The osseous base module does not exist. Please create it first.')
        
        self.base = RebuildObject('skeleton_c_base_000_metaData').rebuild()

        self._rig_module_grp = self._add_module(f'{self._combined_name}_hrc', self.base.modules_grp, True)
        self._ctrls_grp = self._add_module('controls_hrc', self._rig_module_grp, True)
        self._utils_grp = self._add_module('utils_hrc', self._rig_module_grp, True)
        self._annotation_grp = self._add_module('annotations_hrc', self._rig_module_grp, True)

        return
    
    def _create_joints(self):
        """
        Creates joints based on the specified parameters.

        Raises:
            ValueError: If the number of joints is not valid for the specified up type.

        Returns:
            None
        """
        if self._up_type == 'vector_plane':
            if self._num_joints != 3:
                raise ValueError('The number of joints must be 3 for vector plane up type.')
        elif self._up_type == 'object':
            if not self._num_joints > 1:
                raise ValueError('The number of joints must be 2 or greater for object up type.')

        self.c_joints = Joints(self._name, self._side, self._num_joints).create()
        self.c_joints.radius = 0.1
        self._joints = self.c_joints._joints

        [cmds.setAttr(f'{joint.dag_path}.displayLocalAxis', True) for joint in self._joints]

        self._end_joint = self._joints[-1]

        return

    def _parent_joints(self):
        """
        Parents the joints to the parent osseous rig element.
        """
        if self._parent:
            if self._parent.up_type == 'vector_plane' and self._replace_hook == True:
                self._hook_idx = 1

            parent_joint = self._parent.joints[self._hook_idx]
            self._parent_pos = cmds.xform(parent_joint.dag_path, ws=True, translation=True, 
                                        query=True)
            cmds.setAttr(f'{self._joints[0].dag_path}.translate', *self._parent_pos)
            cmds.parent(self._joints[0].dag_path, parent_joint.dag_path)
        else:
            cmds.parent(self._joints[0].dag_path, self.base.root_joint.dag_path)

        return

    def _space_joints(self):
        """
        Adjusts the position and rotation of the joints based on the side attribute.
        """
        x, y, z = self._parent_pos

        if self._side == 'l':
            cmds.xform(self._joints[0].dag_path, ws=True, translation=(x + 5, y, z))
        elif self._side == 'r':
            cmds.xform(self._joints[0].dag_path, ws=True, translation=(x - 5, y, z))
            cmds.setAttr(f'{self._joints[0].dag_path}.rotateY', 180)
        elif self._side == 'c':
            cmds.xform(self._joints[0].dag_path, ws=True, translation=(x, y + 5, z))
            cmds.setAttr(f'{self._joints[0].dag_path}.rotateZ', 90)

        [cmds.setAttr(f'{joint.dag_path}.translateX', 5) for joint in self._joints[1:]]

        return
    
    def _create_aim_joints(self):
        """
        Creates the aim joints for the SkeletonCreator element.
        """
        for joint in self._joints:
            aim_joint = DagNodeData(cmds.duplicate(joint.dag_path, 
                                                   name=f'{joint.dependnode_fn.name()}_aim', 
                                                   parentOnly=True)[0])
            aim_offset = self._add_module(f'{aim_joint.dependnode_fn.absoluteName()}_hrc', 
                                          self._utils_grp, True)
            aim_vectors = self._add_module(f'{aim_joint.dependnode_fn.absoluteName()}_vectors', 
                                           aim_offset, True)

            cmds.matchTransform(aim_offset.dag_path, aim_joint.dag_path)
            cmds.parent(aim_joint.dag_path, aim_vectors.dag_path)

            cmds.parent(cmds.parentConstraint(aim_joint.dag_path, joint.dag_path), 
                        self.base.joints_utils.dag_path)
            
            self._aim_joints.append(aim_joint)
            self._aim_vectors.append(aim_vectors)
            self._aim_offsets.append(aim_offset)

        return

    def _create_controls(self):

        if self._parent:
            self._parent_main_ctrl = RebuildObject(f'{self._parent.main_ctrl.dag_path.partialPathName()}_metaData').rebuild()

        self._main_ctrl = Control(self._name, f'{self._side}', 'main', 0, shape='box').create()
        cmds.matchTransform(self._main_ctrl.offset.dag_path, self._joints[0].dag_path)
        cmds.parent(self._main_ctrl.offset.dag_path, self._ctrls_grp.dag_path)

        if not self._parent:
            cmds.parentConstraint(self.base._root_ctrl.dag_path, 
                                  self._main_ctrl.offset.dag_path, mo=True)
            cmds.scaleConstraint(self.base._root_ctrl.dag_path, 
                                 self._main_ctrl.offset.dag_path, mo=True)
        else:
            cmds.parentConstraint(self._parent_main_ctrl.control.dag_path, 
                                  self._main_ctrl.offset.dag_path, mo=True)

        self._main_ctrl.color = 'red'
        self._main_ctrl.thickness = 2

        if self._up_type == 'vector_plane':
            self._main_ctrl.control.add_attribute('pv_scale', 'float')
            cmds.setAttr(f'{self._main_ctrl.control.dag_path}.pv_scale', 1)

        for i,joint in enumerate(self._joints):

            ctrl = Control(self.name, self.side, 'local', i, shape='orb').create()
            cmds.matchTransform(ctrl.offset.dag_path, joint.dag_path)
            cmds.parent(ctrl.offset.dag_path, self._main_ctrl.control.dag_path)

            cmds.parentConstraint(ctrl.control.dag_path, self._aim_offsets[i].dag_path, mo=True)

            ctrl.color = 'yellow'
            ctrl.thickness = 2

            if self._up_type == 'vector_plane' and i == 1:
                cmds.setAttr(f'{ctrl.offset.dag_path}.translateZ', -0.0001)

            self._ctrls.append(ctrl)

        if self._parent:
            cmds.parentConstraint(self._parent_main_ctrl.control.dag_path, self._main_ctrl.offset.dag_path, mo=True)
            cmds.scaleConstraint(self._parent_main_ctrl.control.dag_path, self._main_ctrl.offset.dag_path, mo=True)

        return
    
    def _create_up_ctrl(self):

        self._up_ctrl = Control(self._name, self._side, 'up', index=0, shape='diamond').create()
        cmds.parent(self._up_ctrl.offset.dag_path, self._main_ctrl.control.dag_path)

        curve = DagNodeData(cmds.curve(d=1, p=[(0, 0, 0), (0, 5, 0)], k=[0, 1]))
        cmds.setAttr(f'{curve.dependnode_fn.absoluteName()}.overrideEnabled', True)
        cmds.setAttr(f'{curve.dependnode_fn.absoluteName()}.overrideDisplayType', 1)
        cmds.parent(curve.dag_path, self._utils_grp.dag_path)

        up_dcm = cmds.createNode('decomposeMatrix', name=f'{self._up_ctrl.control.dependnode_fn.name()}_decomposeMatrix')
        cmds.connectAttr(f'{self._up_ctrl.control.dag_path}.worldMatrix[0]', f'{up_dcm}.inputMatrix')
        cmds.connectAttr(f'{up_dcm}.outputTranslate', f'{curve.shapes[0]}.controlPoints[0]')

        ctrl_dcm = cmds.createNode('decomposeMatrix', name=f'{self._main_ctrl.control.dependnode_fn.name()}_decomposeMatrix')

        if self._up_type == 'vector_plane':
            cmds.connectAttr(f'{self._ctrls[1].control.dag_path}.worldMatrix[0]', f'{ctrl_dcm}.inputMatrix')
            cmds.connectAttr(f'{ctrl_dcm}.outputTranslate', f'{curve.shapes[0]}.controlPoints[1]')
        elif self._up_type == 'object':
            cmds.connectAttr(f'{self._main_ctrl.control.dag_path}.worldMatrix[0]', f'{ctrl_dcm}.inputMatrix')
            cmds.connectAttr(f'{ctrl_dcm}.outputTranslate', f'{curve.shapes[0]}.controlPoints[1]')
    
    def _create_vector_plane_aim_setup(self):
        """
        Creates the aim setup for the vector plane up type.
        """
        output = live_pole_vector_pos(self._ctrls[0].control.dag_path, 
                                self._ctrls[1].control.dag_path, 
                                self._ctrls[-1].control.dag_path, 10)

        cmds.parent(self._up_ctrl.offset.dag_path, self._ctrls_grp.dag_path)
        cmds.connectAttr(f'{output.dependnode_fn.absoluteName()}.output', f'{self._up_ctrl.offset.dag_path}.translate')
        cmds.connectAttr(f'{self._main_ctrl.control.dag_path}.pv_scale', f'{output.dependnode_fn.absoluteName()}.scale')

        cmds.aimConstraint(self._aim_joints[1].dag_path, self._up_ctrl.offset.dag_path,)

        for shape in self._up_ctrl.control.shapes:
            cmds.setAttr(f'{shape}.overrideEnabled', True)
            cmds.setAttr(f'{shape}.overrideDisplayType', 1)
        
        for i, aim_joint in enumerate(self._aim_joints):
            if i < len(self._aim_joints) - 1:
                cmds.aimConstraint(self._aim_vectors[i+1].dag_path, aim_joint.dag_path, 
                                aimVector=(1, 0, 0),
                                worldUpType='object',
                                worldUpObject=self._up_ctrl.control.dag_path, 
                                worldUpVector=(0, 1, 0))
            
            else:
                cmds.aimConstraint(self._aim_vectors[i-1].dag_path, aim_joint.dag_path, 
                                aimVector=(-1, 0, 0),
                                worldUpType='object',
                                worldUpObject=self._up_ctrl.control.dag_path, 
                                worldUpVector=(0, 1, 0))

        return

    def _create_object_aim_setup(self):

        self.previous_vec = None
        self.first_aim_jnt = None
        self.par_aim = None

        cmds.matchTransform(self._up_ctrl.offset.dag_path, self._main_ctrl.control.dag_path)
        up_axis = 'ty' if self._side == 'l' or self.side == 'r' else 'tz'
        cmds.setAttr(f'{self._up_ctrl.control.dag_path}.{up_axis}', 5)

        for i, aim_joint in enumerate(self._aim_joints):
            if i < len(self._aim_joints) - 1:
                cmds.aimConstraint(self._aim_vectors[i+1].dag_path, aim_joint.dag_path, 
                                aimVector=(1, 0, 0),
                                worldUpType='object',
                                worldUpObject=self._up_ctrl.control.dag_path, 
                                worldUpVector=(0, 1, 0))
            else:
                cmds.aimConstraint(self._aim_vectors[i-1].dag_path, aim_joint.dag_path, 
                                aimVector=(-1, 0, 0),
                                worldUpType='object',
                                worldUpObject=self._up_ctrl.control.dag_path, 
                                worldUpVector=(0, 1, 0))

        return

    def _set_replace_hook(self):
            """
            Cleans up the parent metaData node and replaces the last joint, control, and aim joint with the current ones.

            Raises:
                ValueError: If the parent attribute is not set.
            """
            if not self._parent:
                raise ValueError('The replace hook method can only be used if the parent attribute is set.')

            #... Joints cleanup
            transfer_connections(self._parent.joints[-1], self._joints[0], exclude=[])
            cmds.delete(self._parent.joints[-1].dag_path)

            #... Ctrls cleanup
            transfer_connections(self._parent.ctrls[-1], self._ctrls[0].control, exclude=[])
            cmds.delete(self._parent.ctrls[-1].dag_path)

            self._parent.ctrls.pop(-1)

            #... Aim joints cleanup
            transfer_connections(self._parent.aim_joints[-1], self._aim_joints[0])
            transfer_connections(self._parent.aim_offsets[-1], self._aim_offsets[0])
            transfer_connections(self._parent.aim_vectors[-1], self._aim_vectors[0])

            cmds.delete(self._parent.aim_offsets[-1].dag_path)

            self._parent.aim_joints.pop(-1)
            self._parent.aim_offsets.pop(-1)
            self._parent.aim_vectors.pop(-1)

            return

    def _create_meta_data(self):
        super()._create_meta_data()

        self.data['module'] = self._rig_module_grp.dag_path
        self.data['joints'] = [joint.dag_path for joint in self._joints]
        self.data['main_ctrl'] = self._main_ctrl.control.dag_path
        self.data['ctrls'] = [ctrl.control.dag_path for ctrl in self._ctrls]
        self.data['up_ctrl'] = self._up_ctrl.control.dag_path
        self.data['aim_joints'] = [joint.dag_path for joint in self._aim_joints]
        self.data['aim_vectors'] = [vector.dag_path for vector in self._aim_vectors]
        self.data['aim_offsets'] = [offset.dag_path for offset in self._aim_offsets]
        self.data['hook_idx'] = self._hook_idx

        return self.data

    #... Properties ...#
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, value):
        self._parent = self._set_parent(value)

    @property
    def joints(self):
        return self._joints
    
    @joints.setter
    def joints(self, value):
        self._joints = value
    
    @property
    def main_ctrl(self):
        return self._main_ctrl
    
    @main_ctrl.setter
    def main_ctrl(self, value):
        self._main_ctrl = value

    @property
    def up_type(self):
        return self._up_type
    
    @property
    def ctrls(self):
        return self._ctrls
    
    @ctrls.setter
    def ctrls(self, value):
        self._ctrls = value

    @property
    def up_ctrl(self):
        return self._up_ctrl
    
    @up_ctrl.setter
    def up_ctrl(self, value):
        self._up_ctrl = value

    @property
    def aim_joints(self):
        return self._aim_joints
    
    @aim_joints.setter
    def aim_joints(self, value):
        self._aim_joints = value

    @property
    def aim_vectors(self):
        return self._aim_vectors
    
    @aim_vectors.setter
    def aim_vectors(self, value):
        self._aim_vectors = value

    @property
    def aim_offsets(self):
        return self._aim_offsets
    
    @aim_offsets.setter
    def aim_offsets(self, value):
        self._aim_offsets = value
    
    @property
    def hook_idx(self):
        return self._hook_idx
    
    @hook_idx.setter
    def hook_idx(self, value):
        self._hook_idx = value
        

class Osseous(BaseObject):

    def __init__(self,
                 name,
                 side,
                 desc,
                 index,
                 num_joints=1,
                 parent=None,
                 up_type='object'):

        self._name = name
        self._side = side
        self._desc = desc
        self._index = index
        self._num_joints = num_joints
        self._parent = self._set_parent(parent) if parent else None
        self._up_type = up_type

        self._combined_name = f'{self._name}_{self._side}_{self._desc}_{str(self._index).zfill(3)}'

        self._joints = []
        self._end_joint = None

        self._main_ctrl = None
        self._ctrls = []
        self._dummy_ctrl = None
        
        self._parent_pos = [0, 0, 0]

        self._rig_module_grp = None
    
    #... Public Methods ...#
    def create(self):
        """
        Creates the osseous rig module.

        Returns:
            self: Current instance of the class.
        """
        if cmds.objExists(f'{self._combined_name}_metaData'):
            self = MetaNode.rebuild(f'{self._combined_name}_metaData')
        else:
            self._create_module_structure()

            self._create_joints()
            self._parent_joints()
            self._space_joints()
            
            self._create_controls()

            if self._up_type == 'object':
                self._create_object_aim_setup()
            if self._up_type == 'vector_plane':
                self._create_vector_plane_aim_setup()

            self._create_annotations()

            self.data = self._create_meta_data()
            self._create_meta_node(f'{self._combined_name}')

            #self._create_annotations()


        return self
    
    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)

        cls.instance.rig_module = DagNodeData(data['rig_module'])
        cls.instance.main_ctrl = Control(*convert_str_to_list(cmds.getAttr(f'{data["main_ctrl"].name()}.parameters'))).create()
        cls.instance.joints = [DagNodeData(joint) for joint in data['joints']]
        cls.instance.end_joint = DagNodeData(data['end_joint'])
        cls.instance.dummy_ctrl = Control(*convert_str_to_list(cmds.getAttr(f'{data["dummy_ctrl"].name()}.parameters'))).create()

        return cls.instance

    #... Private Methods ...#
    def _set_parent(self, parent):
        """
        Checks if the given parent is a valid Osseous instance.

        Args:
            parent (Osseous): The parent object to be checked.

        Returns:
            bool: True if the parent is valid, False otherwise.

        Raises:
            TypeError: If the parent is not an instance of Osseous.
        """
        parent_instance = Osseous(*convert_str_to_list(cmds.getAttr(f'{parent}.parameters'))).create()

        return parent_instance
    
    def _create_module_structure(self):
        """
        Creates the module structure for the osseous rig.
        """
        if not cmds.objExists('OSSEOUS'):
            raise ValueError('The osseous base module does not exist. Please create it first.')
        
        self.base = OsseousBase().create()

        self._rig_module_grp = self._add_module(f'{self._combined_name}_hrc', self.base.modules_grp, True)
        self._ctrls_grp = self._add_module('controls_hrc', self._rig_module_grp, True)
        self.utils_grp = self._add_module('utils_hrc', self._rig_module_grp, True)
        self.annotation_grp = self._add_module('annotations_hrc', self._rig_module_grp, True)

        return

    def _create_joints(self):
        """
        Creates joints for the osseous rig element.
        """
        if self._up_type == 'vector_plane':
            if self._num_joints > 3 or self._num_joints <= 1:
                raise ValueError('The number of joints must be greater than 1 and less than or equal to 3 for vector plane up type.')

            if self._num_joints == 2:
                self._num_joints = 3
        self.c_joints = Joints(self._name, self._side, self._num_joints).create()
        self.c_joints.radius = 0.1
        self._joints = self.c_joints._joints

        if self._parent and self._parent.dummy_ctrl != None:
            self._joints[0] = self._parent.end_joint
            self._parent._joints.pop(-1)
            cmds.rename(self._joints[0].dag_path, f'{self._name}_{self._side}_{str(self._index).zfill(3)}')

        self.first_joint = self._joints[0].dag_path

        [cmds.setAttr(f'{joint.dag_path}.displayLocalAxis', True) for joint in self._joints]

        self._end_joint = self._joints[-1]

        return

    def _parent_joints(self):
        """
        Parents the joints to the parent osseous rig element.
        """
        if self._parent and not self._parent.dummy_ctrl:
            
            self._parent_pos = cmds.xform(self._parent.end_joint.dag_path, ws=True, translation=True, 
                                        query=True)
            cmds.setAttr(f'{self._joints[0].dag_path}.translate', *self._parent_pos)
            cmds.parent(self.first_joint, self._parent.end_joint.dag_path)
        elif self._parent and self._parent.dummy_ctrl:
            pass
        else:
            cmds.parent(self.first_joint, self.base.root_joint.dag_path)

        return

    def _space_joints(self):
        """
        Adjusts the position and rotation of the joints based on the side attribute.
        """
        x, y, z = self._parent_pos

        if self._parent  and self._parent.dummy_ctrl:
            pass
        else:
            if self._side.lower() == 'l':
                cmds.xform(self.first_joint, ws=True, translation=(x + 5, y, z))
            elif self._side.lower() == 'r':
                cmds.xform(self.first_joint, ws=True, translation=(x - 5, y, z))
                cmds.setAttr(f'{self.first_joint}.rotateY', 180)
            elif self._side.lower() == 'c':
                cmds.xform(self.first_joint, ws=True, translation=(x, y + 5, z))
                cmds.setAttr(f'{self.first_joint}.rotateZ', 90)

            [cmds.setAttr(f'{joint.dag_path}.translateX', 5) for joint in self.c_joints._joints[1:]]

        return
    
    def _create_controls(self):

        self._main_ctrl = Control(self._name, f'{self._side}', 'main', 0, shape='box').create()
        cmds.matchTransform(self._main_ctrl.control.dag_path, self.first_joint)
        cmds.parent(self._main_ctrl.offset.dag_path, self._ctrls_grp.dag_path)

        if self._parent and self._parent.dummy_ctrl:
            cmds.parentConstraint(self._main_ctrl.control.dag_path, self._parent.dummy_ctrl.control.dag_path, mo=True)

        if not self._parent:
            cmds.parentConstraint(self.base._root_ctrl.dag_path, self._main_ctrl.offset.dag_path, mo=True)
            cmds.scaleConstraint(self.base._root_ctrl.dag_path, self._main_ctrl.offset.dag_path, mo=True)

        self._main_ctrl.color = 'red'
        self._main_ctrl.thickness = 2

        if self._up_type == 'vector_plane':
            self._main_ctrl.control.add_attribute('pv_scale', 'float')
            cmds.setAttr(f'{self._main_ctrl.control.dag_path}.pv_scale', 1)

        if self._up_type == 'object':
            self.up_ctrl = Control(self._name, self._side, 'up', 0, shape='diamond').create()
            cmds.matchTransform(self.up_ctrl.offset.dag_path, self._main_ctrl.control.dag_path)
            cmds.parent(self.up_ctrl.offset.dag_path, self._main_ctrl.control.dag_path)
            cmds.setAttr(f'{self.up_ctrl.control.dag_path}.translateY', 5)

        for i,joint in enumerate(self._joints):
            if self._up_type == 'vector_plane' and i == len(self._joints) - 1:
                self._dummy_ctrl = Control(self._name, self._side, 'dummy', i, shape='triangle').create()
                cmds.matchTransform(self._dummy_ctrl.offset.dag_path, joint.dag_path)
                cmds.parent(self._dummy_ctrl.offset.dag_path, self._main_ctrl.control.dag_path)

                self._ctrls.append(self._dummy_ctrl)

                break

            ctrl = Control(self.name, self.side, 'local', i, shape='orb').create()
            cmds.matchTransform(ctrl.offset.dag_path, joint.dag_path)
            cmds.parent(ctrl.offset.dag_path, self._main_ctrl.control.dag_path)

            ctrl.color = 'yellow'
            ctrl.thickness = 2

            self._ctrls.append(ctrl)

        if self._parent:
            cmds.parentConstraint(self._parent._main_ctrl.control.dag_path, self._main_ctrl.offset.dag_path, mo=True)
            cmds.scaleConstraint(self._parent._main_ctrl.control.dag_path, self._main_ctrl.offset.dag_path, mo=True)

        return
    
    def _create_object_aim_setup(self):

        self.previous_vec = None
        self.first_aim_jnt = None
        self.par_aim = None

        up = self.up_ctrl.control.dag_path

        for i, joint in enumerate(self._joints):
            aim_joint = cmds.duplicate(joint.dag_path, name=f'{joint.dependnode_fn.name()}_aim', parentOnly=True)[0]
            aim_offset = self._add_module(f'{aim_joint}_hrc', self.utils_grp, True)
            aim_vectors = self._add_module(f'{aim_joint}_vectors', aim_offset, True)

            cmds.matchTransform(aim_offset.dag_path, aim_joint)
            cmds.parent(aim_joint, aim_vectors.dag_path)

            par_ctrl_aim = cmds.parentConstraint(self._ctrls[i].control.dag_path, aim_offset.dag_path, mo=True)
            par_main = cmds.parentConstraint(aim_joint, joint.dag_path)

            cmds.parent(par_ctrl_aim, par_main, self.base.joints_utils.dag_path)

            #if self.previous_vec:
            cmds.aimConstraint(aim_joint, 
                                self.previous_vec.dag_path, 
                                aimVector=(1, 0, 0),
                                worldUpType='object',
                                worldUpObject=up, 
                                worldUpVector=(0, 1, 0))

            self.previous_vec = aim_vectors

            if not self.first_aim_jnt:
                self.first_aim_jnt = aim_joint


            # self.par_aim = cmds.aimConstraint(self.first_aim_jnt, self._parent.previous_vec.dag_path, 
            #                                 aimVector=(1, 0, 0),
            #                                 worldUpType='object',
            #                                 worldUpObject=up,
            #                                 worldUpVector=(0,1,0))[0]
    
    def _create_vector_plane_aim_setup(self):
        """
        Creates the aim setup for the vector plane up type.
        """
        self.previous_vec = None
        self.first_aim_jnt = None
        self.par_aim = None

        output = live_pole_vector_pos(self._ctrls[0].control.dag_path, 
                                self._ctrls[1].control.dag_path, 
                                self._ctrls[-1].control.dag_path, 10)
        
        up = cmds.spaceLocator()[0]

        cmds.connectAttr(f'{output.dependnode_fn.absoluteName()}.output', f'{up}.translate')
        cmds.connectAttr(f'{self._main_ctrl.control.dag_path}.pv_scale', f'{output.dependnode_fn.absoluteName()}.scale')

        for i, joint in enumerate(self._joints):
            aim_joint = cmds.duplicate(joint.dag_path, name=f'{joint.dependnode_fn.name()}_aim', parentOnly=True)[0]
            aim_offset = self._add_module(f'{aim_joint}_hrc', self.utils_grp, True)
            aim_vectors = self._add_module(f'{aim_joint}_vectors', aim_offset, True)

            cmds.matchTransform(aim_offset.dag_path, aim_joint)
            cmds.parent(aim_joint, aim_vectors.dag_path)

            if self._dummy_ctrl and i == len(self._joints) - 1:
                pass
            else:
                par_main = cmds.parentConstraint(aim_joint, joint.dag_path)
                par_ctrl_aim = cmds.parentConstraint(self._ctrls[i].control.dag_path, aim_offset.dag_path, mo=True)

                cmds.parent(par_ctrl_aim, par_main, self.base.joints_utils.dag_path)

            if self.previous_vec:
                cmds.aimConstraint(aim_joint, 
                                   self.previous_vec.dag_path, 
                                   aimVector=(1, 0, 0),
                                   worldUpType='object',
                                   worldUpObject=up, 
                                   worldUpVector=(0, 1, 0))

            self.previous_vec = aim_vectors

            if not self.first_aim_jnt:
                self.first_aim_jnt = aim_joint

        if self._parent:
            self.par_aim = cmds.aimConstraint(self.first_aim_jnt, self._parent.previous_vec.dag_path, 
                                            aimVector=(1, 0, 0),
                                            worldUpType='object',
                                            worldUpObject=up,
                                            worldUpVector=(0,1,0))[0]

        return
        
    def _create_annotations(self):
            
        for joint in self._joints:
            annotate_node = om.MFnDagNode(DagNodeData(cmds.createNode('annotationShape')).dag_path.transform()).partialPathName()
            
            cmds.setAttr(f'{annotate_node}.text', f'{joint.dag_path.fullPathName().split("|")[-1]}', type='string')
            cmds.setAttr(f'{annotate_node}.displayArrow', 0)
            
            cmds.matchTransform(annotate_node, joint.dag_path)
            cmds.pointConstraint(joint.dag_path, annotate_node)

            cmds.parent(annotate_node, self.annotation_grp.dag_path)

            cmds.setAttr(f'{annotate_node}.v', False)
            
        return
    
    def _create_meta_data(self):
        super()._create_meta_data()

        self.data['parameters'] = convert_list_to_str([self._name,
                                                       self._side,
                                                       self._desc,
                                                       self._index,
                                                       self._num_joints,
                                                       self._parent.meta_node.dependnode_fn.name() if self._parent else None,
                                                       self._up_type])

        self.data['rig_module'] = self._rig_module_grp.dag_path
        self.data['main_ctrl'] = self._main_ctrl.meta_node.dependnode_fn
        self.data['joints'] = [joint.dag_path for joint in self._joints]
        self.data['end_joint'] = self._end_joint.dag_path
        self.data['dummy_ctrl'] = self._dummy_ctrl.meta_node.dependnode_fn if self._dummy_ctrl else None

        return self.data

    #... Properties ...#
    @property
    def num_joints(self):
        return self._num_joints
    
    @num_joints.setter
    def num_joints(self, value):
        self._num_joints = value

    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, value):
        self._parent = self._set_parent(value)

    @property
    def up_type(self):
        return self._up_type
    
    @up_type.setter
    def up_type(self, value):
        self._up_type = value.lower()

    @property
    def rig_module(self):
        return self._rig_module_grp
    
    @rig_module.setter
    def rig_module(self, value):
        self._rig_module_grp = value

    @property
    def main_ctrl(self):
        return self._main_ctrl
    
    @main_ctrl.setter
    def main_ctrl(self, value):
        self._main_ctrl = value

    @property
    def joints(self):
        return self._joints
    
    @joints.setter
    def joints(self, value):
        self._joints = value

    @property
    def end_joint(self):
        return self._end_joint
    
    @end_joint.setter
    def end_joint(self, value):
        self._end_joint = value

    @property
    def dummy_ctrl(self):
        return self._dummy_ctrl
    
    @dummy_ctrl.setter
    def dummy_ctrl(self, value):
        self._dummy_ctrl = value


def live_pole_vector_pos(a, b, c, mult=1.0):
    """
    Calculates the live position of a pole vector based on three input transforms.

    Args:
        a (str): The name of the first transform.
        b (str): The name of the second transform.
        c (str): The name of the third transform.
        mult (float, optional): The multiplier for the pole vector position. Defaults to 1.0.

    Returns:
        DagNodeData: Transform representing the calculated pole vector position.
    """
    a_pos_dcm = cmds.createNode('decomposeMatrix', name='a_pos_dcm')
    b_pos_dcm = cmds.createNode('decomposeMatrix', name='b_pos_dcm')
    c_pos_dcm = cmds.createNode('decomposeMatrix', name='c_pos_dcm')

    cmds.connectAttr(f'{a}.worldMatrix[0]', f'{a_pos_dcm}.inputMatrix')
    cmds.connectAttr(f'{b}.worldMatrix[0]', f'{b_pos_dcm}.inputMatrix')
    cmds.connectAttr(f'{c}.worldMatrix[0]', f'{c_pos_dcm}.inputMatrix')

    vec_ab_pma = cmds.createNode('plusMinusAverage', name='vec_ab_pma')
    vec_ac_pma = cmds.createNode('plusMinusAverage', name='vec_ac_pma')

    cmds.setAttr(f'{vec_ab_pma}.operation', 2)
    cmds.setAttr(f'{vec_ac_pma}.operation', 2)

    cmds.connectAttr(f'{b_pos_dcm}.outputTranslate', f'{vec_ab_pma}.input3D[0]')
    cmds.connectAttr(f'{a_pos_dcm}.outputTranslate', f'{vec_ab_pma}.input3D[1]')

    cmds.connectAttr(f'{c_pos_dcm}.outputTranslate', f'{vec_ac_pma}.input3D[0]')
    cmds.connectAttr(f'{a_pos_dcm}.outputTranslate', f'{vec_ac_pma}.input3D[1]')

    vec_ac_norm_vp = cmds.createNode('vectorProduct', name='vec_ac_norm_vp')

    cmds.setAttr(f'{vec_ac_norm_vp}.operation', 0)
    cmds.setAttr(f'{vec_ac_norm_vp}.normalizeOutput', True)
    cmds.connectAttr(f'{vec_ac_pma}.output3D', f'{vec_ac_norm_vp}.input1')

    vec_ab_scale_vp = cmds.createNode('vectorProduct', name='vec_ab_scale_vp')

    cmds.connectAttr(f'{vec_ab_pma}.output3D', f'{vec_ab_scale_vp}.input1')
    cmds.connectAttr(f'{vec_ac_norm_vp}.output', f'{vec_ab_scale_vp}.input2')

    pos_D = cmds.createNode('multiplyDivide', name='pos_D')

    cmds.connectAttr(f'{vec_ac_norm_vp}.output', f'{pos_D}.input1')
    cmds.connectAttr(f'{vec_ab_scale_vp}.output', f'{pos_D}.input2')

    vec_AD = cmds.createNode('plusMinusAverage', name='vec_AD')

    cmds.setAttr(f'{vec_AD}.operation', 1)

    cmds.connectAttr(f'{pos_D}.output', f'{vec_AD}.input3D[0]')
    cmds.connectAttr(f'{a_pos_dcm}.outputTranslate', f'{vec_AD}.input3D[1]')

    vec_BD = cmds.createNode('plusMinusAverage', name='vec_BD')

    cmds.setAttr(f'{vec_BD}.operation', 2)

    cmds.connectAttr(f'{b_pos_dcm}.outputTranslate', f'{vec_BD}.input3D[0]')
    cmds.connectAttr(f'{vec_AD}.output3D', f'{vec_BD}.input3D[1]')

    vec_bd_norm_vp = cmds.createNode('vectorProduct', name='vec_bd_norm_vp')

    cmds.setAttr(f'{vec_bd_norm_vp}.operation', 0)
    cmds.setAttr(f'{vec_bd_norm_vp}.normalizeOutput', True)
    cmds.connectAttr(f'{vec_BD}.output3D', f'{vec_bd_norm_vp}.input1')

    pole_vec_pos_mult = cmds.createNode('multiplyDivide', name='pole_vec_pos_mult')

    cmds.connectAttr(f'{vec_bd_norm_vp}.output', f'{pole_vec_pos_mult}.input1')
    cmds.setAttr(f'{pole_vec_pos_mult}.input2', mult, mult, mult)

    pos_vec_BD = cmds.createNode('plusMinusAverage', name='pos_vec_AD')

    cmds.connectAttr(f'{b_pos_dcm}.outputTranslate', f'{pos_vec_BD}.input3D[0]')
    cmds.connectAttr(f'{pole_vec_pos_mult}.output', f'{pos_vec_BD}.input3D[1]')

    output = DependencyNodeData(cmds.createNode('network', name='output'))
    output.add_compound_attribute('output', ['X','Y', 'Z'], 'float')
    output.add_attribute('scale', 'float')

    cmds.setAttr(f'{output.dependnode_fn.absoluteName()}.scale', mult)

    cmds.connectAttr(f'{pos_vec_BD}.output3D', f'{output.dependnode_fn.absoluteName()}.output')

    [cmds.connectAttr(f'{output.dependnode_fn.absoluteName()}.scale', f'{pole_vec_pos_mult}.input2{axis}') for axis in 'XYZ']

    return output
