
import maya.cmds as cmds

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

    def create_joints(self):
        """
        Create the joints.
        """
        for i in range(self.num_joints):
            self.joints.append(cmds.createNode('joint',
                                name=f'{self.name.lower()}_{self.side.lower()}_{str(i).zfill(2)}'))
        print(self.joints)
        self._mark_as_joint(self.joints)

        for i in range(len(self.joints) - 1):
            cmds.parent(self.joints[i + 1], self.joints[i])
        return self._joints
    
    def _mark_as_joint(self, joints):

        for joint in joints:
            cmds.addAttr(joint, longName="isJoint", attributeType="bool", defaultValue=True)
            cmds.setAttr(f'{joint}.isJoint', lock=True, keyable=False)