
import maya.cmds as cmds

from dev.utils import convert_list_to_str

from rig.objects.object_data import MetaNode, DagNodeData
from rig.objects.base_object import BaseObject
from rig.joints.joints import Joints
from rig.controls.control import Control

class OsseousBase(BaseObject):

    def __init__(self):

        self._name = 'OSSEOUS'

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
        if cmds.objExists(f'{self._name}_metaData'):
            self = MetaNode.rebuild(f'{self._name}_metaData')
        else:
            self._create_module_structure()
            self._create_root_joint()
            self._create_root_control()

            self.data = self._create_meta_data()
            self._create_meta_node(f'{self._name}')

        return self

    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.joints_grp = DagNodeData(data['joints_grp'])
        cls.instance.joints_utils = DagNodeData(data['joints_utils'])
        cls.instance.modules_grp = DagNodeData(data['modules_grp'])
        cls.instance.controls_grp = DagNodeData(data['controls_grp'])
        cls.instance.root_joint = DagNodeData(data['root_joint'])
        cls.instance.root_ctrl = DagNodeData(data['root_ctrl'])

        return cls.instance
    
    #... Private Methods ...#
    def _create_module_structure(self):

        self._main_grp = self._add_module(self._name)

        self._joints_grp = self._add_module('joints', self._main_grp, True)
        self._joints_utils = self._add_module('joints_utils', self._main_grp, True)
        self._modules_grp = self._add_module('modules', self._main_grp, True)            
        self._controls_grp = self._add_module('controls', self._main_grp, True)

        cmds.setAttr(f'{self._joints_grp.dag_path}.overrideEnabled', True)
        cmds.setAttr(f'{self._joints_grp.dag_path}.overrideDisplayType', 2)

    def _create_root_joint(self):
        """
        Creates the root joint for the osseous rig element.
        """
        self._root_joint = Joints('root', 'c', 1).create()
        cmds.parent(self._root_joint.joints[0].dag_path, self._joints_grp.dag_path)

        self._root_joint.radius = 0.1

        return

    def _create_root_control(self):
        """
        Creates the root control for the osseous rig element.
        """
        #if not ou.node_with_attr(self._root_joint, 'isControl'):
        self._root_ctrl = Control('root', 'c', 'main', 0, 'circle').create()
        print(self._root_ctrl.control.dag_path)
        #self._root_ctrl.match_transforms(self._root_joint, 'isJoint')
        cmds.parent(self._root_ctrl.offset.dag_path, self.controls_grp.dag_path)
        cmds.parentConstraint(self._root_ctrl.control.dag_path, self._root_joint.joints[0].dag_path, mo=True)

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


class Osseous(BaseObject):

    def __init__(self, name, side, desc, index, num_joints=1, parent=None):

        self._name = name
        self._side = side
        self._desc = desc
        self._index = index
        self._num_joints = num_joints
        self._parent = parent

        self._combined_name = f'{self._name}_{self._side}_{self._desc}_{str(self._index).zfill(3)}'

        self._joints = []

        self._ctrls = []
        
        self._parent_pos = [0, 0, 0]

        self._rig_module_grp = None
        self._end_joint = None
    
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

            self._create_aim_setup()

            self.data = self._create_meta_data()
            self._create_meta_node(f'{self._combined_name}')

            #self._create_annotations()


        return self
    
    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.rig_module = DagNodeData(data['rig_module'])
        cls.instance.end_joint = DagNodeData(data['end_joint'])

        return cls.instance

    #... Private Methods ...#
    def _check_parent(self, parent):
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
            if not isinstance(parent, Osseous):
                raise TypeError('The parent attribute must be an Osseous instance')

        return True
    
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
        self.c_joints = Joints(self._name, self._side, self._num_joints).create()
        self.c_joints.radius = 0.1
        self._joints = self.c_joints._joints

        self.first_joint = self._joints[0].dag_path
        
        cmds.parent(self.first_joint, self.base.joints_grp.dag_path)

        [cmds.setAttr(f'{joint.dag_path}.displayLocalAxis', True) for joint in self._joints]

        self._end_joint = self._joints[-1]

        return

    def _parent_joints(self):
        """
        Parents the joints to the parent osseous rig element.
        """
        if self._parent:
            self._parent_pos = cmds.xform(self._parent.end_joint.dag_path, ws=True, translation=True, 
                                        query=True)
            cmds.setAttr(f'{self._joints[0].dag_path}.translate', *self._parent_pos)
            cmds.parent(self.first_joint, self._parent.end_joint.dag_path)

        else:
            cmds.parent(self.first_joint, self.base.root_joint.dag_path)

        return

    def _space_joints(self):
        """
        Adjusts the position and rotation of the joints based on the side attribute.
        """
        x, y, z = self._parent_pos

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

        self.main_ctrl = Control(self._name, f'{self._side}', 'main', 0, shape='box').create()
        cmds.matchTransform(self.main_ctrl.control.dag_path, self.first_joint)
        cmds.parent(self.main_ctrl.offset.dag_path, self._ctrls_grp.dag_path)
        if not self._parent:
            print(self.base._root_ctrl.dag_path)
            cmds.parentConstraint(self.base._root_ctrl.dag_path, self.main_ctrl.offset.dag_path, mo=True)
            cmds.scaleConstraint(self.base._root_ctrl.dag_path, self.main_ctrl.offset.dag_path, mo=True)

        self.main_ctrl.color = 'red'
        self.main_ctrl.thickness = 2

        self.up_ctrl = Control(self._name, self._side, 'up', 0, shape='diamond').create()
        cmds.matchTransform(self.up_ctrl.offset.dag_path, self.main_ctrl.control.dag_path)
        cmds.parent(self.up_ctrl.offset.dag_path, self.main_ctrl.control.dag_path)
        cmds.setAttr(f'{self.up_ctrl.control.dag_path}.translateY', 5)

        for i,joint in enumerate(self._joints):
            ctrl = Control(self.name, self.side, 'local', i, shape='orb').create()
            cmds.matchTransform(ctrl.offset.dag_path, joint.dag_path)
            cmds.parent(ctrl.offset.dag_path, self.main_ctrl.control.dag_path)

            ctrl.color = 'yellow'
            ctrl.thickness = 2

            self._ctrls.append(ctrl)

        if self._parent:
            cmds.parentConstraint(self._parent.main_ctrl.control.dag_path, self.main_ctrl.offset.dag_path, mo=True)
            cmds.scaleConstraint(self._parent.main_ctrl.control.dag_path, self.main_ctrl.offset.dag_path, mo=True)

        return
    
    def _create_aim_setup(self):

        self.previous_vec = None
        self.first_aim_jnt = None
        self.par_aim = None
        for i, joint in enumerate(self._joints):
            aim_joint = cmds.duplicate(joint.dag_path, name=f'{joint.dependnode_fn.name()}_aim', parentOnly=True)[0]
            aim_offset = self._add_module(f'{aim_joint}_hrc', self.utils_grp, True)
            aim_vectors = self._add_module(f'{aim_joint}_vectors', aim_offset, True)

            cmds.matchTransform(aim_offset.dag_path, aim_joint)
            cmds.parent(aim_joint, aim_vectors.dag_path)

            par_ctrl_aim = cmds.parentConstraint(self._ctrls[i].control.dag_path, aim_offset.dag_path, mo=True)
            par_main = cmds.parentConstraint(aim_joint, joint.dag_path)

            cmds.parent(par_ctrl_aim, par_main, self.base.joints_utils.dag_path)

            if self.previous_vec:
                cmds.aimConstraint(aim_joint, 
                                   self.previous_vec.dag_path, 
                                   aimVector=(1, 0, 0),
                                   worldUpType='object',
                                   worldUpObject=self.up_ctrl.control.dag_path, 
                                   worldUpVector=(0, 1, 0))

            self.previous_vec = aim_vectors

            if not self.first_aim_jnt:
                self.first_aim_jnt = aim_joint

        if self._parent:
            self.par_aim = cmds.aimConstraint(self.first_aim_jnt, self._parent.previous_vec.dag_path, 
                                            aimVector=(1, 0, 0),
                                            worldUpType='object',
                                            worldUpObject=self._parent.up_ctrl.control.dag_path,
                                            worldUpVector=(0,1,0))[0]
        
    def _create_annotations(self):
            
        for joint in self._joints:
            joint = ou.node_with_attr(joint, 'isJoint')
            annotate_node = cmds.createNode('annotationShape')
            annotate_node = cmds.listRelatives(annotate_node, parent=True)[0]
            
            cmds.setAttr(f'{annotate_node}.text', f'{joint.split("|")[-1]}', type='string')
            cmds.setAttr(f'{annotate_node}.displayArrow', 0)
            
            cmds.matchTransform(annotate_node, joint)
            cmds.pointConstraint(joint, annotate_node)

            cmds.parent(annotate_node, self.annotation_grp)

            cmds.setAttr(f'{annotate_node}.v', False)
            
        return
    
    def _create_meta_data(self):
        super()._create_meta_data()

        self.data['parameters'] = convert_list_to_str([self._name,self._side,self._num_joints,self._parent])

        self.data['rig_module'] = self._rig_module_grp.dag_path
        self.data['end_joint'] = self._end_joint.dag_path

        return self.data

    #... Properties ...#
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value.lower()

    @property
    def side(self):
        return self._side
    
    @side.setter
    def side(self, value):
        self._side = value.upper()
    
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
        if self._check_parent(value):
            self._parent = value
        else:
            self._parent = None

    @property
    def joints(self):
        return self._joints
    
    @joints.setter
    def joints(self, value):
        self._joints = value

    @property
    def rig_module(self):
        return self._rig_module_grp
    
    @rig_module.setter
    def rig_module(self, value):
        self._rig_module_grp = value

    @property
    def end_joint(self):
        return self._end_joint
    
    @end_joint.setter
    def end_joint(self, value):
        self._end_joint = value
    
    

