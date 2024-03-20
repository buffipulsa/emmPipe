
import maya.cmds as cmds

from ..joints.joints import Joints
from ..controls.control import Control
from ..objects import object_utils

class Osseous:

    def __init__(self, side, name, joints_num, parent=None):
        
        self._side = side.lower()
        self._name = name.lower()
        self._joints_num = joints_num

        self._parent = parent if self._check_parent(parent) else None

        self._root_joint = 'root_c_00'

        self._joints = []
        self._parent_joint = None

        self._has_end_joint = False

        self.parent_pos = [0, 0, 0]
    
    @property
    def side(self):
        return self._side
    
    @property
    def name(self):
        return self._name
    
    @property
    def joints_num(self):
        return self._joints_num
    
    @property
    def joints(self):
        return self._joints
    
    @joints.setter
    def joints(self, value):
        self._joints = value
    
    @property
    def parent_joint(self):
        return self._parent_joint
    
    @property
    def has_end_joint(self):
        return self._has_end_joint

    def create(self):
        """
        Creates the osseous rig module.

        Returns:
            self: Current instance of the class.
        """
            
        self._create_module_structure()

        self._create_root_joint()
        self._create_joints()
        self._parent_joints()
        self._space_joints()
        
        self._create_controls()

        self._create_annotations()

        self._create_osseous_attributes()
        self._set_osseous_attributes()

        return self
    
    def root_joint(self, index):
        """
        Sets the root joint of the current joint chain.

        Args:
            index (int): The index of the root joint in the list of joints.

        Returns:
            self: Returns the current instance of the class.
        """
        if self._parent:
            self._parent_joint = self._parent.joints[index]
        else:
            raise ValueError(f'The instance {self.__class__.__name__}.{self._name} has no parent')
        
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
        top_grp = 'OSSEOUS'
        self.joints_grp = 'joints'
        if not cmds.objExists(top_grp):
            top_grp = cmds.createNode('transform', name=top_grp)
        if not cmds.objExists(self.joints_grp):
            self.joints_grp = cmds.createNode('transform', name=self.joints_grp)
            cmds.parent(self.joints_grp, top_grp)
            cmds.setAttr(f'{self.joints_grp}.template', True)
            

        self._module_grp = cmds.createNode('transform', name=f'{self._side}_{self._name}_osseous')
        cmds.parent(self._module_grp, top_grp)

        self._ctrls_grp = cmds.createNode('transform', name=f'{self._side}_{self._name}_controls')
        cmds.parent(self._ctrls_grp, self._module_grp)

        self.annotation_grp = cmds.createNode('transform', name=f'{self._side}_{self._name}_annotations')
        cmds.parent(self.annotation_grp, self._module_grp)

        return

    def _create_root_joint(self):
        """
        Creates the root joint for the osseous rig element.
        """
        if not cmds.objExists(self._root_joint):
            self._root_jnt = cmds.createNode('joint', name=self._root_joint)
            cmds.parent(self._root_jnt, self.joints_grp)

        return


    def _create_joints(self):
        """
        Creates joints for the osseous rig element.
        """
        self.c_joints = Joints(self._side, self._name, self._joints_num).create()
        self._joints = self.c_joints.joints

        self.first_joint = self._joints[0]
        if self._parent and not self._parent_joint:
            self._parent_joint = self._parent.joints[-1]
        
        cmds.parent(self.first_joint, self.joints_grp)

        return

    def _parent_joints(self):
        """
        Parents the joints to the parent osseous rig element.
        """
        if self._parent is not None:
            end_joint = object_utils.node_with_attr(self._parent_joint, 'isJoint')
            self.parent_pos = cmds.xform(end_joint, ws=True, translation=True, 
                                        query=True)
            cmds.setAttr(f'{self._joints[0]}.translate', *self.parent_pos)
            cmds.parent(self.first_joint, end_joint)

        jnts_in_grp = cmds.listRelatives(self.joints_grp)
        if len(jnts_in_grp) == 2:
            cmds.parent(jnts_in_grp[1], jnts_in_grp[0])

        return

    def _space_joints(self):
        """
        Adjusts the position and rotation of the joints based on the side attribute.
        """
        if self._side.lower() == 'l':
            cmds.xform(self.first_joint, ws=True, 
                       translation=(self.parent_pos[0]+5, 
                       self.parent_pos[1], 
                       self.parent_pos[2]))
        elif self._side.lower() == 'r':
            cmds.xform(self.first_joint, ws=True, 
                       translation=(self.parent_pos[0]-5, 
                       self.parent_pos[1], 
                       self.parent_pos[2]))
            cmds.setAttr(f'{self.first_joint}.rotateY', 180)
        elif self._side.lower() == 'c':
            cmds.xform(self.first_joint, ws=True, 
                       translation=(self.parent_pos[0], 
                       self.parent_pos[1]+5, 
                       self.parent_pos[2]))
            cmds.setAttr(f'{self.first_joint}.rotateZ', 90)

        for joint in self.c_joints.joints[1:]:
            cmds.setAttr(f'{joint}.translateX', 5)

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

        return
    
    def _create_annotations(self):
            
        for joint in self._joints:
            joint = object_utils.node_with_attr(joint, 'isJoint')
            annotate_node = cmds.createNode('annotationShape')
            annotate_node = cmds.listRelatives(annotate_node, parent=True)[0]
            
            cmds.setAttr(f'{annotate_node}.text', f'{joint.split("|")[-1]}', type='string')
            cmds.setAttr(f'{annotate_node}.displayArrow', 0)
            
            cmds.matchTransform(annotate_node, joint)
            cmds.pointConstraint(joint, annotate_node)

            cmds.parent(annotate_node, self.annotation_grp)
            
        return
    
    def _create_osseous_attributes(self):

        node = object_utils.node_by_type(self.first_joint, 'joint')    

        cmds.addAttr(node, longName="isOsseuos", attributeType="bool", defaultValue=True)
        cmds.setAttr(f'{node}.isOsseuos', lock=True, keyable=False)

        attrs = [f'oss{attr.capitalize()}' for attr in ['side', 'name']] 
        for attr in attrs:
            cmds.addAttr(node, longName=attr, dataType='string')
        
        return

    def _set_osseous_attributes(self):

        node = object_utils.node_with_attr(self.first_joint, 'isJoint')
        cmds.setAttr(f'{node}.ossSide', self._side, type='string')
        cmds.setAttr(f'{node}.ossName', self._name, type='string')

        return
    

