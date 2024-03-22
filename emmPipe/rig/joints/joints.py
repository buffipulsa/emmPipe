
import maya.cmds as cmds

from ..objects import object_utils as ou

class Joints:
    """
    Represents a joint chain in the scene.
    """

    def __init__(self, side='l', name='temp', num_joints=1):
        """
        Initialize the Joints instance.

        Args:
            name (str): The name of the joint chain.
            num_joints (int): The number of joints to create.

        Raises:
            TypeError: If no name is assigned.
        """

        if not name:
            raise TypeError('No name assigned')

        self._side = side
        self._name = name
        self._num_joints = num_joints
        self._joints = []

        self._radius = 1.0

    @property
    def side(self):
        """
        str: The side of the joint chain.
        """
        return self._side
    
    @property
    def name(self):
        """
        str: The name of the joint chain.
        """
        return self._name

    @property
    def num_joints(self):
        """
        int: The number of joints to create.
        """
        return self._num_joints

    @property
    def joints(self):
        """
        list: The joint chain.
        """
        return self._joints
    
    @property
    def radius(self):
        """
        float: The radius of the joints.
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        """
        Set the radius of the joints.

        Args:
            value (float): The radius of the joints.
        """
        [cmds.setAttr(f'{joint}.radius', value) for joint in self._joints if len(self._joints) > 0]
        self._radius = value

    def create(self):
        """
        Create the joints.
        """
        self._joints = [cmds.createNode('joint', \
            name=f'{self.name.lower()}_{self.side.lower()}_{str(i).zfill(2)}') \
            for i in range(self.num_joints)]

        self._mark_as_joint(self._joints)
        self._mark_joint_index(self._joints)

        [cmds.parent(self._joints[i + 1], self._joints[i]) for i in range(len(self._joints) - 1)]
        
        return self
    
    def _mark_as_joint(self, joints):

        for joint in joints:
            cmds.addAttr(joint, longName="isJoint", attributeType="bool", defaultValue=True)
            cmds.setAttr(f'{joint}.isJoint', lock=True, keyable=False)
    
    def _mark_joint_index(self, joints):
        
        for i, joint in enumerate(joints):
            cmds.addAttr(ou.node_with_attr(joint, 'isJoint'), longName='jointIndex', attributeType='long')
            cmds.setAttr(f'{ou.node_with_attr(joint, "isJoint")}.jointIndex', i)
