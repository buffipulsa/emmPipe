import maya.cmds as cmds
import maya.api.OpenMaya as om

from dev.utils import convert_list_to_str, convert_str_to_list

from rig.objects.object_data import DagNodeData
from rig.objects.object_data import MetaNode
from rig.objects.base_object import BaseObject

class RigModule(BaseObject):

    data = {}

    def __init__(self, name) -> None:
        super().__init__()
        
        self._name = name

        self._module = None
        self._systems = None
        self._joints = None
        self._fk = None
        self._ik = None
        self._constraints = None
        self._par_constraints = None
        self._point_constraints = None
        self._orient_constraints = None
        self._scale_constraints = None

        self._meta_node = None

    def create(self):

        self.initialize_modules()
        self.data = self.create_meta_data()
        self.create_meta_node()

        return self

    @property
    def meta_node(self):
        return self._meta_node
    
    @meta_node.setter
    def meta_node(self, value):
        self._meta_node = value

    @property
    def name(self):
        return self._name
    
    @property
    def module(self):
        return self._module
    
    @module.setter
    def module(self, value):
        self._module = value

    @property
    def systems(self):
        return self._systems
    
    @systems.setter
    def systems(self, value):
        self._systems = value

    @property
    def constraints(self):
        return self._constraints
    
    @constraints.setter
    def constraints(self, value):
        self._constraints = value

    @property
    def joints(self):
        return self._joints
    
    @joints.setter
    def joints(self, value):
        self._joints = value

    @property
    def fk(self):
        return self._fk
    
    @fk.setter
    def fk(self, value):
        self._fk = value

    @property
    def ik(self):
        return self._ik
    
    @ik.setter
    def ik(self, value):
        self._ik = value
    
    @property
    def par_constraints(self):
        return self._par_constraints
    
    @par_constraints.setter
    def par_constraints(self, value):
        self._par_constraints = value
    
    @property
    def point_constraints(self):
        return self._point_constraints
    
    @point_constraints.setter
    def point_constraints(self, value):
        self._point_constraints = value
    
    @property
    def orient_constraints(self):
        return self._orient_constraints
    
    @orient_constraints.setter
    def orient_constraints(self, value):
        self._orient_constraints = value
    
    @property
    def scale_constraints(self):
        return self._scale_constraints
    
    @scale_constraints.setter
    def scale_constraints(self, value):
        self._scale_constraints = value

    def initialize_modules(self):

        self.module = self.add_module(f'{self.name}_module')
        self.systems = self.add_module('systems', parent=self.module)
        self.constraints = self.add_module('constraints', parent=self.module)

        self.joints = self.add_module('joints', parent=self.systems)
        self.fk = self.add_module('fk', parent=self.systems)
        self.ik = self.add_module('ik', parent=self.systems)

        self.par_constraints = self.add_module('parent_constraints', parent=self.constraints)
        self.point_constraints = self.add_module('point_constraints', parent=self.constraints)
        self.orient_constraints = self.add_module('orient_constraints', parent=self.constraints)
        self.scale_constraints = self.add_module('scale_constraints', parent=self.constraints)

    
    def add_module(self, name, parent=None, vis_switch=True):
        
        module = DagNodeData(cmds.createNode('transform', name=f'{name}'))

        if parent:
            cmds.parent(module.dag_path, parent.dag_path)

            if vis_switch:
                vis_name = f'{module.transform_fn.name()}_vis'
                cmds.addAttr(parent.dag_path, longName=vis_name, attributeType='bool', keyable=True)
                cmds.setAttr(f'{parent.dag_path}.{vis_name}', 1)

                cmds.connectAttr(f'{parent.dag_path}.{vis_name}', f'{module.dag_path}.visibility')
        
        return module
    
    def create_meta_data(self):
        super().create_meta_data()
        
        self.data['parameters'] = convert_list_to_str([self.name])
        
        self.data['module'] = self.module.dag_path
        self.data['systems'] = self.systems.dag_path
        self.data['constraints'] = self.constraints.dag_path
        self.data['joints'] = self.joints.dag_path
        self.data['fk'] = self.fk.dag_path
        self.data['ik'] = self.ik.dag_path
        self.data['par_constraints'] = self.par_constraints.dag_path
        self.data['point_constraints'] = self.point_constraints.dag_path
        self.data['orient_constraints'] = self.orient_constraints.dag_path
        self.data['scale_constraints'] = self.scale_constraints.dag_path

        return self.data
    

    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.module = DagNodeData(data['module'])
        cls.instance.systems = DagNodeData(data['systems'])
        cls.instance.joints = DagNodeData(data['joints'])
        cls.instance.fk = DagNodeData(data['fk'])
        cls.instance.ik = DagNodeData(data['ik'])
        cls.instance.constraints = DagNodeData(data['constraints'])
        cls.instance.par_constraints = DagNodeData(data['par_constraints'])
        cls.instance.point_constraints = DagNodeData(data['point_constraints'])
        cls.instance.orient_constraints = DagNodeData(data['orient_constraints'])
        cls.instance.scale_constraints = DagNodeData(data['scale_constraints'])

        return cls.instance

