import maya.cmds as cmds
import maya.api.OpenMaya as om

from dev.utils import convert_list_to_str, convert_str_to_list

from rig.objects.object_data import DagNodeData, DependencyNodeData
from rig.objects.object_utils import MetaNode

class RigModule:

    data = {}

    def __init__(self, name) -> None:
        
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
        
        data = {}
        data['class_module'] = str(self.__class__.__module__)
        data['class_name'] = str(self.__class__.__name__)
        data['parameters'] = convert_list_to_str([self.name])
        
        data['module'] = self.module.dag_path
        data['systems'] = self.systems.dag_path
        data['constraints'] = self.constraints.dag_path
        data['joints'] = self.joints.dag_path
        data['fk'] = self.fk.dag_path
        data['ik'] = self.ik.dag_path
        data['par_constraints'] = self.par_constraints.dag_path
        data['point_constraints'] = self.point_constraints.dag_path
        data['orient_constraints'] = self.orient_constraints.dag_path
        data['scale_constraints'] = self.scale_constraints.dag_path

        return data
    
    def create_meta_node(self):

        self._meta_node = MetaNode(self.name, self.data).name

    @classmethod
    def from_data(cls, meta_node, data):

        instance = cls(*convert_str_to_list(data['parameters']))
        instance.meta_node = meta_node
        
        instance.module = DagNodeData(data['module'])
        instance.systems = DagNodeData(data['systems'])
        instance.joints = DagNodeData(data['joints'])
        instance.fk = DagNodeData(data['fk'])
        instance.ik = DagNodeData(data['ik'])
        instance.constraints = DagNodeData(data['constraints'])
        instance.par_constraints = DagNodeData(data['par_constraints'])
        instance.point_constraints = DagNodeData(data['point_constraints'])
        instance.orient_constraints = DagNodeData(data['orient_constraints'])
        instance.scale_constraints = DagNodeData(data['scale_constraints'])

        return instance


class SerializeMetaNode:
    
        ATTR_SKIPTS = ['message','caching','frozen','isHistoricallyInteresting',
                        'nodeState','binMembership','affects','affectedBy']

        def __init__(self, meta_node) -> None:
            
            self.meta_node = DependencyNodeData(meta_node)

            self._data = {}
            
            self.seriazlie_data()

        @property
        def data(self):
            return self._data
    
        def seriazlie_data(self):
            
            attrs_mobj = [self.meta_node.dependnode_fn.attribute(attr) for attr in cmds.listAttr(self.meta_node.dependnode_fn.absoluteName())\
                      if attr not in self.ATTR_SKIPTS]
            
            attrs_fn = [attr.apiTypeStr for attr in attrs_mobj]
            
            for attr, attr_fn in zip(attrs_mobj, attrs_fn):
                attr_name = self.get_attribute_name(attr)
   
                if attr_fn == 'kMessageAttribute':
                    self._data[attr_name] = self.serialize_message_attr(attr)
                if attr_fn == 'kTypedAttribute':
                    self._data[attr_name] = self.serialize_typed_attr(attr)
                if attr_fn == 'kNumericAttribute':
                    self._data[attr_name] = self.serialize_numeric_attr(attr)

        def get_attribute_name(self, attr):
            return self.meta_node.dependnode_fn.findPlug(attr, True).partialName()
        
        def serialize_message_attr(self, attr):
                
                message_plug = self.meta_node.dependnode_fn.findPlug(attr, True)
                connected_node = message_plug.connectedTo(True,False)[0].node()

                connected_node = DagNodeData(om.MFnDagNode(connected_node).fullPathName())

                return connected_node.dag_path

        def serialize_typed_attr(self, attr):
            
            string_plug = self.meta_node.dependnode_fn.findPlug(attr, True)
 
            return string_plug.asString()
    
        def serialize_numeric_attr(self, attr):
                
            numeric_plug = self.meta_node.dependnode_fn.findPlug(attr, True)
            
            return numeric_plug.asFloat()
        

class RebuildObject(SerializeMetaNode):

    def __init__(self, meta_node) -> None:
        super().__init__(meta_node)
        
        self.meta_node = meta_node

        self._class = self._get_class()

    def _get_class(self):
        
        class_module = self.data['class_module']
        class_name = self.data['class_name']
        
        module = __import__(class_module, fromlist=[class_name])
        
        class_ = getattr(module, class_name)
        
        return class_
    
    def rebuild(self):

        class_instance = self._class.from_data(self.meta_node, self.data)
            
        return class_instance
