
import maya.cmds as cmds

from ..joints.joints import Joints
from ..controls.control import Control

class Osseous:

    def __init__(self):

        self._name = None
        self.side = None
        self._num_joints = 1
        self._parent = None

        self._root_joint = 'root_c_00'

        self._joints = []
        self._parent_joint = None

        self._ctrls = []
        
        self.parent_pos = [0, 0, 0]
    
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
    def parent_joint(self):
        return self._parent_joint

    def create(self):
        """
        Creates the osseous rig module.

        Returns:
            self: Current instance of the class.
        """
            
        self._create_module_structure()

        self._create_root_joint()
        self._create_root_control()
        self._create_joints()
        self._parent_joints()
        self._space_joints()
        
        self._create_controls()

        self.create_aim_setup()

        self._create_annotations()

        self._create_osseous_attributes()
        self._set_osseous_attributes()

        return self
    
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
        if parent is not None:
            if not isinstance(parent, Osseous):
                raise TypeError('The parent attribute must be an Osseous instance')
                return False

        return True
    
    def _create_module_structure(self):
        """
        Creates the module structure for the osseous rig.
        """
        self.top_grp = 'OSSEOUS'
        self.joints_grp = 'joints'
        self.joints_utils = f'{self.joints_grp}_utils'
        if not cmds.objExists(self.top_grp):
            self.top_grp = cmds.createNode('transform', name=self.top_grp)
        if not cmds.objExists(self.joints_grp):
            self.joints_grp = cmds.createNode('transform', name=self.joints_grp)
            self.joints_utils = cmds.createNode('transform', name=self.joints_utils)
            cmds.parent(self.joints_grp, self.joints_utils, self.top_grp)
            
            cmds.setAttr(f'{self.joints_grp}.overrideEnabled', True)
            cmds.setAttr(f'{self.joints_grp}.overrideDisplayType', 2)
            

        self._module_grp = cmds.createNode('transform', name=f'{self._name}_{self._side}_osseous_hrc')
        cmds.parent(self._module_grp, self.top_grp)

        self._ctrls_grp = cmds.createNode('transform', name=f'{self._name}_{self._side}_controls_hrc')
        cmds.parent(self._ctrls_grp, self._module_grp)

        self.utils_grp = cmds.createNode('transform', name=f'{self._name}_{self._side}_utils_hrc')
        cmds.parent(self.utils_grp, self._module_grp)

        self.annotation_grp = cmds.createNode('transform', name=f'{self._name}_{self._side}_annotations_hrc')
        cmds.parent(self.annotation_grp, self._module_grp)

        return

    def _create_root_joint(self):
        """
        Creates the root joint for the osseous rig element.
        """
        if not cmds.objExists(self._root_joint):
            self._root_jnt = Joints('c', 'root', 1).create()
            cmds.parent(self._root_jnt.joints[0], self.joints_grp)

            self._root_jnt.radius = 0.1

        return

    def _create_root_control(self):
        """
        Creates the root control for the osseous rig element.
        """
        if not ou.node_with_attr(self._root_joint, 'isControl'):
            self._root_ctrl = Control('c', 'root', scale=100, shape='COG').create()
            self._root_ctrl.match_transforms(self._root_joint, 'isJoint')
            cmds.parent(self._root_ctrl.os_grp, self.top_grp)
            cmds.parentConstraint(self._root_ctrl.ctrl, ou.node_with_attr(self._root_joint, 'isJoint'), mo=True)

        return

    def _create_joints(self):
        """
        Creates joints for the osseous rig element.
        """
        self.c_joints = Joints(self._side, self._name, self._num_joints).create()
        self.c_joints.radius = 0.1
        self._joints = self.c_joints._joints

        self.first_joint = self._joints[0]
        if self._parent and not self._parent_joint:
            self._parent_joint = self._parent.joints[-1]
        
        cmds.parent(self.first_joint, self.joints_grp)

        [cmds.setAttr(f'{joint}.displayLocalAxis', True) for joint in self._joints]

        return

    def _parent_joints(self):
        """
        Parents the joints to the parent osseous rig element.
        """
        if self._parent is not None:
            end_joint = ou.node_with_attr(self._parent_joint, 'isJoint')
            self.parent_pos = cmds.xform(end_joint, ws=True, translation=True, 
                                        query=True)
            cmds.setAttr(f'{self._joints[0]}.translate', *self.parent_pos)
            cmds.parent(self.first_joint, end_joint)

        #... CHECK FOR FASTER WAY TO DO THIS
        jnts_in_grp = ou.nodes_with_attr('isJoint')
        if len(jnts_in_grp) == 2:
            cmds.parent(jnts_in_grp[1], jnts_in_grp[0])

        return

    def _space_joints(self):
        """
        Adjusts the position and rotation of the joints based on the side attribute.
        """
        x, y, z = self.parent_pos

        if self._side == 'L':
            cmds.xform(self.first_joint, ws=True, translation=(x + 5, y, z))
        elif self._side == 'R':
            cmds.xform(self.first_joint, ws=True, translation=(x - 5, y, z))
            cmds.setAttr(f'{self.first_joint}.rotateY', 180)
        elif self._side == 'C':
            cmds.xform(self.first_joint, ws=True, translation=(x, y + 5, z))
            cmds.setAttr(f'{self.first_joint}.rotateZ', 90)

        [cmds.setAttr(f'{joint}.translateX', 5) for joint in self.c_joints._joints[1:]]

        return
    
    def _create_controls(self):

        self.main_ctrl = Control(self.side, f'main_{self.name}', scale=100, shape='box').create()
        self.main_ctrl.match_transforms(self.first_joint, 'isJoint')
        cmds.parent(self.main_ctrl.os_grp, self._ctrls_grp)

        self.main_ctrl.color = 'red'
        self.main_ctrl.thickness = 2

        for joint in self._joints:
            ctrl = Control(self.side, self.name, scale=50, shape='orb').create()
            ctrl.match_transforms(joint, 'isJoint')
            cmds.parent(ctrl.os_grp, self.main_ctrl.ctrl)

            ctrl.color = 'yellow'
            ctrl.thickness = 2

            self._ctrls.append(ctrl)

        if self._parent:
            cmds.parentConstraint(self._parent.main_ctrl.ctrl, self.main_ctrl.os_grp, mo=True)

        return
    
    def create_aim_setup(self):

        self.previous_vec = None
        self.first_aim_jnt = None
        self.par_aim = None
        for i, joint in enumerate(self._joints):
            aim_joint = cmds.duplicate(ou.node_with_attr(joint, 'isJoint'), \
                                       name=f'{joint}_aim', parentOnly=True)[0]
            aim_offset = cmds.createNode('transform', name=f'{aim_joint}_offset')
            aim_vectors = cmds.createNode('transform', name=f'{aim_joint}_vectors')
            cmds.parent(aim_vectors, aim_offset)
            cmds.matchTransform(aim_offset, aim_joint)
            cmds.parent(aim_joint, aim_vectors)

            
            par_ctrl_aim = cmds.parentConstraint(self._ctrls[i].ctrl, aim_offset)
            par_main = cmds.parentConstraint(aim_joint, ou.node_with_attr(joint, 'isJoint'))

            cmds.parent(par_ctrl_aim, par_main, self.joints_utils)

            cmds.setAttr(f'{aim_offset}.v', False)

            if self.previous_vec:
                cmds.aimConstraint(aim_joint, self.previous_vec, aimVector=(0, 1, 0),
                                   worldUpType='vector', worldUpVector=(0, 0, 1))

            self.previous_vec = aim_vectors

            if not self.first_aim_jnt:
                self.first_aim_jnt = aim_joint

            

        if self._parent:
            if self._parent_joint == self._parent._joints[-1]:
                #print(self._parent_joint, '--->', self._parent._joints[-1])
                self.par_aim = cmds.aimConstraint(self.first_aim_jnt, self._parent.previous_vec, 
                                                aimVector=(0, 1, 0),
                                                worldUpType='vector', 
                                                worldUpVector=(0, 0, 1))[0]
            else:
                print(self._parent_joint, '--->', self._parent._joints[-1])


        def list_aim_constraint_nodes(aim_constraint):
            connected_nodes = cmds.listConnections(aim_constraint, type="transform", source=True, destination=True)
            return [node for node in connected_nodes if cmds.objectType(node) == "aimConstraint"]

        
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
    
    def _create_osseous_attributes(self):

        node = ou.node_by_type(self.first_joint, 'joint')    

        cmds.addAttr(node, longName="isOsseuos", attributeType="bool", defaultValue=True)
        cmds.setAttr(f'{node}.isOsseuos', lock=True, keyable=False)

        attrs = [f'oss{attr.capitalize()}' for attr in ['side', 'name']] 
        [cmds.addAttr(node, longName=attr, dataType='string') for attr in attrs]
        
        return

    def _set_osseous_attributes(self):

        node = ou.node_with_attr(self.first_joint, 'isJoint')
        cmds.setAttr(f'{node}.ossSide', self._side, type='string')
        cmds.setAttr(f'{node}.ossName', self._name, type='string')

        return
    

