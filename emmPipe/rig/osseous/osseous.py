
import maya.cmds as cmds

from ..joints.joints import Joints

class Osseous:

    def __init__(self, side, name, joints_num, parent=None):
        
        self._side = side.lower()
        self._name = name.lower()
        self._joints_num = joints_num

        self._parent = parent if self._check_parent(parent) else None

        self._joints = []

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

    def create(self):
        
        self.create_module_structure()

        self.create_joints()
        self.parent_joints()
        self.space_joints()
        


        self.create_osseous_attributes()
        self.set_osseous_attributes()

        return
    
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
    
    def create_module_structure(self):
        """
        Creates the module structure for the osseous rig.
        """
        top_grp = 'OSSEOUS'
        self.joints_grp = 'joints'
        if not cmds.objExists(top_grp):
            top_grp = cmds.createNode('transform', name=top_grp)
        if not cmds.objExists(self.joints_grp):
            joints_grp = cmds.createNode('transform', name=self.joints_grp)
            cmds.parent(self.joints_grp, top_grp)

        self._module_grp = cmds.createNode('transform', name=f'{self._side}_{self._name}_OSSEOUS')

        cmds.parent(self._module_grp, top_grp)

        return

    def create_joints(self):
        """
        Creates joints for the osseous rig element.
        """
        self.c_joints = Joints(self._side, self._name, self._joints_num)
        self._joints = self.c_joints.create_joints()

        self.first_joint = self._joints[0]

        cmds.parent(self.first_joint, self.joints_grp)

        return

    def parent_joints(self):
        """
        Parents the joints to the parent osseous rig element.
        """
        if self._parent is not None:
            
            self.parent_pos = cmds.xform(self._parent.joints[-1], ws=True, translation=True, 
                                        query=True)
            cmds.setAttr(f'{self._joints[0]}.translate', *self.parent_pos)
            cmds.parent(self.first_joint, self._parent.joints[-1])

        return

    def space_joints(self):
        """
        Adjusts the position and rotation of the joints based on the side attribute.
        """
        for joint in self._joints[1:]:
            cmds.setAttr(f'{joint}.translateX', 5)

        if self._side.lower() == 'l':
            #cmds.setAttr(f'{self.first_joint}.translateX', 2)
            cmds.xform(self.first_joint, ws=True, 
                       translation=(self.parent_pos[0]+2, 
                       self.parent_pos[1], 
                       self.parent_pos[2]))
        elif self._side.lower() == 'r':
            cmds.xform(self.first_joint, ws=True, 
                       translation=(self.parent_pos[0]-2, 
                       self.parent_pos[1], 
                       self.parent_pos[2]))
            cmds.setAttr(f'{self.first_joint}.rotateY', 180)
            #cmds.setAttr(f'{first_joint}.rotateZ', 180)
        elif self._side.lower() == 'c':
            cmds.xform(self.first_joint, ws=True, 
                       translation=(self.parent_pos[0], 
                       self.parent_pos[1], 
                       self.parent_pos[2]))
            cmds.setAttr(f'{self.first_joint}.rotateZ', 90)

        return
    
    def create_osseous_attributes(self):

        cmds.addAttr(self.first_joint, longName="isOsseuos", attributeType="bool", defaultValue=True)
        cmds.setAttr(f'{self.first_joint}.isOsseuos', lock=True, keyable=False)

        attrs = [f'oss{attr.capitalize()}' for attr in ['side', 'name']] 
        for attr in attrs:
            cmds.addAttr(self.first_joint, longName=attr, dataType='string')

    def set_osseous_attributes(self):

        cmds.setAttr(f'{self.first_joint}.ossSide', self._side, type='string')
        cmds.setAttr(f'{self.first_joint}.ossName', self._name, type='string')

        return


