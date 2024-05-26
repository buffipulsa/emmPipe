import maya.cmds as cmds
import maya.api.OpenMaya as om

from dev.utils import convert_list_to_str, convert_str_to_list

from rig.objects.object_data import DagNodeData
from rig.objects.object_data import MetaNode
from rig.objects.base_object import BaseObject
from rig.controls.control import Control

class RigContrainer(BaseObject):
    """
    Represents a rig container that contains modules, controls, and metadata.

    Methods:
        Public:
        create(): Creates the rig container.
        from_data(cls, meta_node, data): Creates an instance of the class using the provided data.

        Private:
        _initialize_modules(): Initializes the modules for the rig container.
        _create_controls(): Creates and sets up controls for the rig container.
        _set_type_meta(value): Sets the 'type' attribute of the meta node.
        _create_meta_data(): Creates metadata for the rig container.

    Properties:
        name (str): The name of the rig container.
        type (str): The type of the rig container.
        top_node (DagNodeData): The top node of the rig container.
        geometry (DagNodeData): The geometry module of the rig container.
        controls (DagNodeData): The controls module of the rig container.
        modules (DagNodeData): The modules module of the rig container.
    """
    def __init__(self, name) -> None:
        super().__init__()

        self._name = name

        self._type = 'chr'
        self._top_node = None
        self._geometry = None
        self._controls = None
        self._modules = None

    #... PUBLIC METHODS ...#
    def create(self):
        """
        Creates the module.

        If the metadata for the module already exists, it rebuilds the module using the existing metadata.
        Otherwise, it initializes the modules, creates the controls, creates the metadata, and creates the meta node.

        Returns:
            self: The created instance of the class.
        """      
        if cmds.objExists(f'{self._name}_metaData'):
            self = MetaNode.rebuild(f'{self._name}_metaData')
        else:
            self._initialize_modules()
            self._create_controls()

            self.data = self._create_meta_data()
            self._create_meta_node(self._name)

        return self

    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.type = data['type']
        cls.instance.top_node = DagNodeData(data['top_node'])
        cls.instance.geometry = DagNodeData(data['geometry'])
        cls.instance.controls = DagNodeData(data['controls'])
        cls.instance.modules = DagNodeData(data['modules'])

        return cls.instance
    
    #... PRIVATE METHODS ...#
    def _initialize_modules(self):
        """
        Initializes the modules for the rig container.

        Returns:
            None
        """
        self._top_node = self._add_module(self.name)
        self._geometry = self._add_module('geometry', self._top_node)
        self._controls = self._add_module('controls', self._top_node)
        self._modules = self._add_module('modules', self._top_node)

    def _create_controls(self):
        """
        Creates and sets up controls for the rig container.

        Returns:
            None
        """
        global_ctrl = Control('global', 'c', '0', 'arrow1way').create()
        layout_ctrl = Control('layout', 'c', '0', 'circle').create()
        local_ctrl = Control('local', 'c', '0', 'circle').create()

        global_ctrl.scale = 10
        layout_ctrl.scale = global_ctrl.scale - (0.2 * global_ctrl.scale)
        local_ctrl.scale = layout_ctrl.scale - (0.2 * layout_ctrl.scale)

        cmds.parent(global_ctrl.offset.dag_path, self._controls.dag_path)
        cmds.parent(layout_ctrl.offset.dag_path, global_ctrl.control.dag_path)
        cmds.parent(local_ctrl.offset.dag_path, layout_ctrl.control.dag_path)

    def _set_type_meta(self, value):
        """
        Sets the 'type' attribute of the meta node.

        Args:
            value (str): The value to set for the 'type' attribute.

        Returns:
            None
        """
        if hasattr(self, 'meta_node'):
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.type', 
                         lock=False, type='string')
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.type', 
                         value, lock=True, type='string')

    def _create_meta_data(self):
        super()._create_meta_data()
        
        self.data['type'] = self.type
        self.data['parameters'] = convert_list_to_str([self.name])

        self.data['top_node'] = self._top_node.dag_path
        self.data['geometry'] = self._geometry.dag_path
        self.data['controls'] = self._controls.dag_path
        self.data['modules'] = self._modules.dag_path

        return self.data

    #... PROPERTIES ...#
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        self._type = value
        self._set_type_meta(value)

    @property
    def top_node(self):
        return self._top_node
    
    @top_node.setter
    def top_node(self, value):
        self._top_node = value

    @property
    def geometry(self):
        return self._geometry
    
    @geometry.setter
    def geometry(self, value):
        self._geometry = value

    @property
    def controls(self):
        return self._controls
    
    @controls.setter
    def controls(self, value):
        self._controls = value
    
    @property
    def modules(self):
        return self._modules
    
    @modules.setter
    def modules(self, value):
        self._modules = value


class RigModule(BaseObject):
    """
    Represents a rig module that contains systems, joints, constraints, and other components necessary for its operation.

    Methods:
        Public:
        create(): Creates the module.
        from_data(cls, meta_node, data): Creates an instance of the class using the provided data.

        Private:
        _initialize_modules(): Initializes the modules for the rig module.
        _create_meta_data(): Creates metadata for the rig module.

    Attributes:
        name (str): The name of the rig module.
        module (DagNode): The module node representing the rig module.
        systems (DagNode): The systems node representing the systems within the rig module.
        constraints (DagNode): The constraints node representing the constraints within the rig module.
        joints (DagNode): The joints node representing the joints within the rig module.
        fk (DagNode): The fk node representing the fk controls within the rig module.
        ik (DagNode): The ik node representing the ik controls within the rig module.
        par_constraints (DagNode): The parent constraints node representing the parent constraints within the rig module.
        point_constraints (DagNode): The point constraints node representing the point constraints within the rig module.
        orient_constraints (DagNode): The orient constraints node representing the orient constraints within the rig module.
        scale_constraints (DagNode): The scale constraints node representing the scale constraints within the rig module.
    """
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

    #... PUBLIC METHODS ...#
    def create(self):
        """
        Creates the module.

        If the metadata for the module already exists, it rebuilds the module using the existing metadata.
        Otherwise, it initializes the modules, creates the metadata, and creates the meta node.

        Returns:
            self: The created instance of the class.
        """
        if cmds.objExists(f'{self._name}_metaData'):
            self = MetaNode.rebuild(f'{self._name}_metaData')
        else:
            self._initialize_modules()
            self.data = self._create_meta_data()
            self._create_meta_node(self._name)

        return self

    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.module = DagNodeData(data['module'])
        cls.instance.systems = DagNodeData(data['systems'])
        cls.instance.constraints = DagNodeData(data['constraints'])

        return cls.instance

    #... PRIVATE METHODS ...#
    def _initialize_modules(self):
        """
        Initializes the modules for the rig module.

        Returns:
            None
        """
        self.module = self._add_module(f'{self.name}_module')
        if cmds.objExists('modules'):
            cmds.parent(self.module.dag_path, 'modules')

        self.systems = self._add_module('systems', parent=self.module)
        self.constraints = self._add_module('constraints', parent=self.module)

        self.joints = self._add_module('joints', parent=self.systems)
        self.fk = self._add_module('fk', parent=self.systems)
        self.ik = self._add_module('ik', parent=self.systems)

        self.par_constraints = self._add_module('parent_constraints', parent=self.constraints)
        self.point_constraints = self._add_module('point_constraints', parent=self.constraints)
        self.orient_constraints = self._add_module('orient_constraints', parent=self.constraints)
        self.scale_constraints = self._add_module('scale_constraints', parent=self.constraints)
    
    def _create_meta_data(self):
        super()._create_meta_data()
        
        self.data['parameters'] = convert_list_to_str([self.name])
        
        self.data['module'] = self.module.dag_path
        self.data['systems'] = self.systems.dag_path
        self.data['constraints'] = self.constraints.dag_path

        return self.data

    #... PROPERTIES ...#
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

