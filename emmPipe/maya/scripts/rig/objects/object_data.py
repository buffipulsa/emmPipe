
import importlib

import maya.api.OpenMaya as om
import maya.cmds as cmds


class DependencyNodeData:
    """
    A class that represents a dependency node in Maya.

    Properties:
        m_obj (om.MObject): The MObject associated with the selected object.
        dependnode_fn (om.MFnDependencyNode): The MFnDependencyNode object associated with the current object.

    Raises:
        TypeError: If no node is assigned.
        ValueError: If the node is a DAG node.
    """
    def __init__(self, node=None):
        """
        Initializes a new instance of the DependencyNodeData class.

        Args:
            node (str): The name of the node to assign.

        Raises:
            TypeError: If no node is assigned.
        """
        if not node:
            raise TypeError('No node assigned')
        
        self.selection = om.MSelectionList()
        self.selection.add(node)

        self._m_obj = self._get_m_obj()
        
        self._dependnode_fn = self._get_dependnode_fn()

        self._check_if_dag_or_depend_node()

    #... Public methods ...#
    def add_attribute(self, attr_name, attr_type, keyable=True):
        """
        Adds an attribute to the node.
        """
        data = {'int': {'attr_fn': om.MFnNumericAttribute(), 'data_type': om.MFnNumericData.kInt},
                'float': {'attr_fn': om.MFnNumericAttribute(), 'data_type': om.MFnNumericData.kFloat},
                'string': {'attr_fn': om.MFnTypedAttribute(), 'data_type': om.MFnData.kString}}

        attr_fn = data[attr_type]['attr_fn']
        data_type = data[attr_type]['data_type']

        attr = attr_fn.create(attr_name, attr_name, data_type)
        attr_fn.storable = True
        attr_fn.writable = True
        attr_fn.keyable = keyable
        self._dependnode_fn.addAttribute(attr)
        
    def add_compound_attribute(self, name, attr_names, attr_type, keyable=True):
        """
        Adds a compound attribute to the node.
        """
        data = {'int': {'attr_fn': om.MFnNumericAttribute(), 'data_type': om.MFnNumericData.kInt},
                'float': {'attr_fn': om.MFnNumericAttribute(), 'data_type': om.MFnNumericData.kFloat},
                'string': {'attr_fn': om.MFnTypedAttribute(), 'data_type': om.MFnData.kString}}

        compound_fn = om.MFnCompoundAttribute()
        compound_attr = compound_fn.create(name, name, )        

        for attr_name in attr_names:
            attr_fn = data[attr_type]['attr_fn']
            data_type = data[attr_type]['data_type']
            attr = attr_fn.create(f'{name}{attr_name}', f'{name}{attr_name}', data_type)
            attr_fn.storable = True
            attr_fn.writable = True
            attr_fn.keyable = keyable
            compound_fn.addChild(attr)
        
        self._dependnode_fn.addAttribute(compound_attr)

    #... Private methods ...#
    def _check_if_dag_or_depend_node(self):
        """
        Checks if the node is a DAG node or a dependency node.
        
        Raises a ValueError if the node is a DAG node, suggesting the use of the DagNodeData class instead.
        """
        try:
            if self.selection.getDagPath(0).isValid():
                raise ValueError(f'{self._dependnode_fn.name()} is a DAG node. Please use the DagNodeData class instead.')
        except:
            return False

    def _get_m_obj(self):
        """
        Get the MObject associated with the selected object.

        Returns:
            MObject: The MObject associated with the selected object.
        """
        self._m_obj = self.selection.getDependNode(0)
        return self._m_obj
    
    def _get_dependnode_fn(self):
        """
        Returns the MFnDependencyNode object associated with the current object.

        Returns:
            om.MFnDependencyNode: The MFnDependencyNode object.
        """
        self._dependnode_fn = om.MFnDependencyNode(self._m_obj)
        return self._dependnode_fn

    #... Properties ...#
    @property
    def m_obj(self):
        """
        Returns the MObject associated with this object.

        Returns:
            MObject: The MObject associated with this object.
        """
        self._m_obj = self._get_m_obj()

        return self._m_obj
    
    @property
    def dependnode_fn(self):
        """
        Returns the MFnDependencyNode object associated with this object.

        Returns:
            om.MFnDependencyNode: The MFnDependencyNode object.
        """
        self._dependnode_fn = self._get_dependnode_fn()

        return self._dependnode_fn


class DagNodeData(DependencyNodeData):
    """
    A class representing data for a DAG node in Maya.

    Properties:
        shapes (list): A list of shape nodes attached to the object.
        shapes_fn (list): A list of function sets for the shape nodes.
        transform_fn (om.MFnTransform): The function set for the transform node.
        vtx_component (list): A list of vertex components for the shape nodes.
        vtx_ids (list): A list of vertex IDs for the shape nodes.
        vtx_counts (list): A list of vertex counts for the shape nodes.
        dag_path (om.MDagPath): The MDagPath for the node.
    
    Raises:
        ValueError: If the node is a DEPENDENCY node.
    """

    def __init__(self, node=None):
        """
        Initialize the DagNodeData instance.

        Args:
            node (str): The name of the node.

        Raises:
            TypeError: If no node is assigned.
        """
        super().__init__(node=node)

        self._shapes = []
        self._shapes_fn = []
        self._transform_fn = None
        self._vtx_components = []
        self._vtx_ids = []
        self._vtx_counts = []

        self._dag_path = self._get_dag_path()

        if self._dag_path:
            self._transform_fn = self._get_transform_fn()
            self._shapes = self._get_shapes()

            if self._shapes:
                self._shapes_fn = self._get_shapes_fn()
                self._vtx_component = self._get_vtx_component()
                self._vtx_ids = self._get_vtx_ids()
                self._vtx_counts = self._get_vtx_counts()

    #... Private methods ...#
    def _check_if_dag_or_depend_node(self):
        """
        Checks if the node is a DAG node or a dependency node.

        Raises:
            ValueError: If the node is a dependency node.
        """
        if not self.selection.getDagPath(0).isValid():
            raise ValueError(f'{self._dependnode_fn.name()} is a Dependency node. Please use the DependencyNodeData class instead.')

    def _get_dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.

        Raises:
            ValueError: If no valid dag path is found for the node.
        """
        if self.selection.getDagPath(0).isValid():
            return self.selection.getDagPath(0)
        else:
            raise ValueError('No valid dag path found for {}'.format(self.dependnode_fn.name()))

        return False

    def _get_shapes(self):
        """
        Returns a list of shape nodes attached to the object.

        Returns:
            list: A list of shape nodes attached to the object.

        Raises:
            ValueError: If the object has no shape node.
        """
        if self._shapes:
            self._shapes.clear()

        if self._dag_path.childCount():
            for i in range(self._dag_path.childCount()):
                child_mobj = self._dag_path.child(i)
                if child_mobj.hasFn(om.MFn.kShape) and not om.MFnDagNode(child_mobj).isIntermediateObject:
                    shape_dag_path = om.MFnDagNode(child_mobj).getPath()
                    self._shapes.append(shape_dag_path)

            return self._shapes
        else:        
            return None
        
    def _get_transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        if self._dag_path.apiType() == om.MFn.kTransform:
            self._transform_fn = om.MFnTransform(self._dag_path)

        return self._transform_fn

    def _get_shapes_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        self._shapes_fn.clear()

        if self._shapes:
            for shape in self._shapes:
                if shape.hasFn(om.MFn.kMesh):
                    fn_set = om.MFnMesh(self.dag_path)

                elif shape.hasFn(om.MFn.kNurbsCurve):
                    fn_set = om.MFnNurbsCurve(self.dag_path)

                elif shape.hasFn(om.MFn.kNurbsSurface):
                    fn_set = om.MFnNurbsSurface(self.dag_path)
                else:
                    return None
                
                fn_set.setObject(shape)
                self._shapes_fn.append(fn_set)

            return self._shapes_fn
        
        else:
            return None
        
    def _get_vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        self._vtx_components.clear()

        if self.shapes_fn:
            for shape_fn in self._shapes_fn:
                if shape_fn.type() == om.MFn.kMesh:
                    comp = om.MFnSingleIndexedComponent()
                    vtx_component = comp.create(om.MFn.kMeshVertComponent)
                    comp.setCompleteData(shape_fn.numVertices)

                if shape_fn.type() == om.MFn.kNurbsCurve:
                    comp = om.MFnSingleIndexedComponent()
                    vtx_component = comp.create(om.MFn.kCurveCVComponent)
                    comp.setCompleteData(shape_fn.numCVs)

                if shape_fn.type() == om.MFn.kNurbsSurface:
                    comp = om.MFnDoubleIndexedComponent()
                    vtx_component = comp.create(om.MFn.kSurfaceCVComponent)
                    comp.setCompleteData(shape_fn.numCVsInU, shape_fn.numCVsInV)

                self._vtx_components.append(vtx_component)

            return self._vtx_components

        else:
            return None
        
    def _get_vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        self._vtx_ids.clear()
        
        if self.shapes_fn:
            for shape_fn in self._shapes_fn:
                if shape_fn.type() == om.MFn.kMesh:
                    self._vtx_id = range(0, len(cmds.ls('{}.vtx[*]'.format(self.dependnode_fn.name()), fl=True)))
                else:
                    self._vtx_id = range(0, len(cmds.ls('{}.cv[*]'.format(self.dependnode_fn.name()), fl=True)))

                self._vtx_ids.append(self._vtx_id)

            return self._vtx_ids
        
        else:
            return None
        
    def _get_vtx_counts(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
        self._vtx_counts.clear()

        if self.vtx_ids:
            for vtx_id in self._vtx_ids:
                vtx_count = len(vtx_id)

                self._vtx_counts.append(vtx_count)

            return self._vtx_counts
    
        else:
            return None

    #... Properties ...#
    @property
    def dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.
        """
        self._dag_path = self._get_dag_path()
        return self._dag_path
        
    @property
    def shapes(self):
        """
        Retrieves the shape node for the node.

        Returns:
            List[om.MObject]: List of shape nodes for the node.
        """
        self._shapes = self._get_shapes()
        return self._shapes

    @property
    def transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        self._transform_fn = self._get_transform_fn()
        return self._transform_fn
    
    @property
    def shapes_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        self._shapes_fn = self._get_shapes_fn()
        return self._shapes_fn

    @property
    def vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        self._vtx_component = self._get_vtx_component()
        return self._vtx_component
    
    @property
    def vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        self._vtx_ids = self._get_vtx_ids()
        return self._vtx_ids
    
    @property
    def vtx_counts(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
        self._vtx_counts = self._get_vtx_count()
        return self._vtx_counts


class MetaNode:
    """
    Represents a meta node in Maya.

    Attributes:
        _name (str): The name of the meta node.
        data (dict): The data associated with the meta node.
        meta_node (str): The name of the created network node.
    """

    def __init__(self, name, data) -> None:
        """
        Initializes a new instance of the MetaNode class.

        Args:
            name (str): The name of the meta node.
            data (dict): The data associated with the meta node.
        """
        self._name = name.replace('_metaData', '') if name.endswith('_metaData') else name
        self.data = data

        self.meta_node = cmds.createNode('network', name=f'{self._name}_metaData')

        self._create_attrs()

    #... Private methods ...#
    def _create_attrs(self):
        """
        Creates attributes on the meta node based on the provided data.
        """
        node_data = DependencyNodeData(self.meta_node)

        type_to_attr_fn = {
            str: [om.MFnTypedAttribute, om.MFnData.kString, 'setString'],
            int: [om.MFnNumericAttribute, om.MFnNumericData.kInt, 'setInt'],
            float: [om.MFnNumericAttribute, om.MFnNumericData.kFloat, 'setFloat'],
        }

        for attr_name, data in self.data.items():
            attr_name = f'__{attr_name}'
            if type(data) in type_to_attr_fn:
                attr_fn, data_fn, plug_function = type_to_attr_fn[type(data)]

                attr_mobj = attr_fn().create(attr_name, attr_name, data_fn)
                node_data.dependnode_fn.addAttribute(attr_mobj)

                set_attr_function = getattr(node_data.dependnode_fn.findPlug(attr_name, True), plug_function)
                set_attr_function(data)

                cmds.setAttr(f'{self.meta_node}.{attr_name}', lock=True)

            else:
                if type(data) == list:
                    compound_attr = om.MFnCompoundAttribute()
                    compound_attr_mobj = compound_attr.create(attr_name, attr_name)

                    for i, item in enumerate(data):
                        message_attr_mobj = om.MFnMessageAttribute().create(f'{attr_name}_{i}', f'{attr_name}_{i}')
                        compound_attr.addChild(message_attr_mobj)

                    node_data.dependnode_fn.addAttribute(compound_attr_mobj)

                    for i, item in enumerate(data):
                        cmds.connectAttr(f'{item.fullPathName()}.message', f'{self.meta_node}.{attr_name}_{i}')

                elif type(data) == om.MDagPath:
                    message_attr_mobj = om.MFnMessageAttribute().create(attr_name, attr_name)
                    node_data.dependnode_fn.addAttribute(message_attr_mobj)

                    cmds.connectAttr(f'{data.fullPathName()}.message', f'{self.meta_node}.{attr_name}')

                elif type(data) == om.MFnDependencyNode:
                    message_attr_mobj = om.MFnMessageAttribute().create(attr_name, attr_name)
                    node_data.dependnode_fn.addAttribute(message_attr_mobj)

                    cmds.connectAttr(f'{data.name()}.message', f'{self.meta_node}.{attr_name}')

    #... Properties ...#
    @property
    def name(self):
        """
        Gets the name of the meta node.

        Returns:
            str: The name of the meta node.
        """
        return self.meta_node

    
class DeserializeMetaNode:
    """
    A class that deserializes meta nodes in Maya.

    Methods:
        __init__(self, meta_node): Initializes a new instance of the DeserializeMetaNode class.
        seriazlie_data(self): Serializes the data from the meta node.
        get_attribute_name(self, attr): Gets the attribute name from the given attribute.
        deserialize_message_attr(self, attr): Deserializes a message attribute.
        deserialize_typed_attr(self, attr): Deserializes a typed attribute.
        deserialize_numeric_attr(self, attr): Deserializes a numeric attribute.
        _get_class(self): Gets the class from the serialized data.
        rebuild(self): Rebuilds the class instance from the serialized data.
    """
    def __init__(self, meta_node) -> None:
        """
        Initializes a new instance of the DeserializeMetaNode class.

        Args:
            meta_node: The meta node to deserialize.
        """
        self.meta_node = DependencyNodeData(meta_node)
        self._data = {}

        self._deseriazlie_data()
        self._class = self._get_class()

    #... Private methods ...#
    def _deseriazlie_data(self):
        """
        Deserializes the data from the meta node.
        """
        attrs_mobj = [self.meta_node.dependnode_fn.attribute(attr) for attr in cmds.listAttr(self.meta_node.dependnode_fn.absoluteName())]
        attrs_fn = [attr.apiTypeStr for attr in attrs_mobj]
        
        for attr, attr_fn in zip(attrs_mobj, attrs_fn):
            try:
                if om.MFnAttribute(attr).name.startswith('__'):
                    attr_name = self._get_attribute_name(attr)

                    if attr_fn == 'kCompoundAttribute':
                        self._data[attr_name] = self._deserialize_compound_attr(attr)
                    if attr_fn == 'kMessageAttribute':
                        self._data[attr_name] = self._deserialize_message_attr(attr)
                    if attr_fn == 'kTypedAttribute':
                        self._data[attr_name] = self._deserialize_typed_attr(attr)
                    if attr_fn == 'kNumericAttribute':
                        self._data[attr_name] = self._deserialize_numeric_attr(attr)
            except:
                pass

    def _get_attribute_name(self, attr):
        """
        Gets the attribute name from the given attribute.

        Args:
            attr: The attribute.

        Returns:
            The attribute name.
        """
        return self.meta_node.dependnode_fn.findPlug(attr, True).partialName().replace('__','')
    
    def _deserialize_compound_attr(self, attr):
        """
        Deserializes a compound attribute.

        Args:
            attr: The attribute.

        Returns:
            The deserialized compound attribute.
        """
        compound_plug = self.meta_node.dependnode_fn.findPlug(attr, True)
        compound_data = []

        for i in range(compound_plug.numChildren()):
            child_name = compound_plug.child(i).partialName()

            compound_data.append(self._deserialize_message_attr(child_name))
    
        return compound_data

    def _deserialize_message_attr(self, attr):
        """
        Deserializes a message attribute.

        Args:
            attr: The attribute.

        Returns:
            The deserialized message attribute.
        """
        message_plug = self.meta_node.dependnode_fn.findPlug(attr, True)
        connected_node = message_plug.connectedTo(True,False)[0].node()

        try:
            connected_node = DagNodeData(om.MFnDagNode(connected_node).fullPathName())

            return connected_node.dag_path
        except:
            connected_node = DependencyNodeData(om.MFnDependencyNode(connected_node).name())

            return connected_node.dependnode_fn


    def _deserialize_typed_attr(self, attr):
        """
        Deserializes a typed attribute.

        Args:
            attr: The attribute.

        Returns:
            The deserialized typed attribute.
        """
        string_plug = self.meta_node.dependnode_fn.findPlug(attr, True)

        return string_plug.asString()

    def _deserialize_numeric_attr(self, attr):
        """
        Deserializes a numeric attribute.

        Args:
            attr: The attribute.

        Returns:
            The deserialized numeric attribute.
        """
        numeric_plug = self.meta_node.dependnode_fn.findPlug(attr, True)
        
        return numeric_plug.asFloat()
    
    def _get_class(self):
        """
        Gets the class from the serialized data.

        Returns:
            The class.
        """
        class_module = self.data['class_module']
        class_name = self.data['class_name']
        
        module = __import__(class_module, fromlist=[class_name])
        
        class_ = getattr(module, class_name)
    
        return class_

    #... Properties ...#
    @property
    def data(self):
        """
        Gets the serialized data.

        Returns:
            The serialized data.
        """
        return self._data
    

class RebuildObject:
    """
    Class that rebuilds objects based on meta data from metaNodes.
    """
    def __repr__(self):
        return f'{self._class}'

    def __init__(self, meta_node):
        self._meta_node = meta_node
        self._meta_data = DeserializeMetaNode(self._meta_node).data

        self._class_call = self._meta_data['parameters']

    def rebuild(self):
        """
        Rebuilds an instance of the object based on the stored metadata.

        Returns:
            instance: The rebuilt instance of the object.
        """
        mod = __import__(self._meta_data['class_module'], fromlist=[self._meta_data['class_name']])
        globals()[self._meta_data['class_name']] = getattr(mod, self._meta_data['class_name'])
        instance = eval(self._class_call)

        for attr, value in self._meta_data.items():
            attr = attr.replace('__','')
            if attr not in ['class_module', 'class_name', 'parameters']:
                if type(value) == om.MDagPath:
                    setattr(instance, attr, DagNodeData(value))
                elif type(value) == om.MFnDependencyNode:
                    setattr(instance, attr, DependencyNodeData(value))
                elif type(value) == list:
                    values = []
                    for val in value:
                        if type(val) == om.MDagPath:
                            values.append(DagNodeData(val))
                        elif type(val) == om.MFnDependencyNode:
                            values.append(DependencyNodeData(val))
                        elif type(val) == DagNodeData:
                            values.append(DagNodeData(val))
                    
                    setattr(instance, attr, values)
        
        instance.meta_node = self._meta_node
                    
        return instance
