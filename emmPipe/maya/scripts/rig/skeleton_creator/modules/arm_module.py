
from rig.osseous.osseous import Osseous
from rig.objects.base_object import BaseObject

class ArmModule:

    def __init__(self, name, side, desc, index, num_joints=1, parent=None):
        super().__init__()

        self._name = name
        self._side = side
        self._desc = desc
        self._index = index
        self._num_joints = num_joints
        self._parent = parent

        self._arm_module = Osseous(self._name, self._side, 
                               self._desc, self._index, 
                               self._num_joints, None).create()
        
        self._wrist_module = Osseous(self._name, self._side, 
                               self._desc, self._index, 
                               self._num_joints, self._arm_module).create()
        