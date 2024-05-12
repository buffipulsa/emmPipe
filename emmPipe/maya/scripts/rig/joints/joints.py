
import maya.cmds as cmds

from rig.objects.object_data import DagNodeData

class Joints:
    """
    Represents a joint chain in the scene.
    """

    def __init__(self, name, side, num_joints=1):
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
        if not side:
            raise TypeError('No side assigned')

        self._name = name
        self._side = side
        self._num_joints = num_joints

        self._combined_name = f'{name.lower()}_{side.lower()}'
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
        [cmds.setAttr(f'{joint.dag_path}.radius', value) for joint in self._joints if len(self._joints) > 0]
        self._radius = value

    def create(self):
        """
        Create the joints.
        """
        self._joints = [DagNodeData(cmds.createNode('joint', \
            name=f'{self._combined_name}_{str(i).zfill(2)}')) \
            for i in range(self.num_joints)]


        [cmds.parent(self._joints[i + 1].dag_path, self._joints[i].dag_path) for i in range(len(self._joints) - 1)]
        
        return self
