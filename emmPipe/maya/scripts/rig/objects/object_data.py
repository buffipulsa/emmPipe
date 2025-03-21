
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

        try:
            self._m_obj = om.MSelectionList().add(node).getDependNode(0)
        except RuntimeError:
            raise ValueError(f'No valid node found for {node}')

        self._dependnode_fn = om.MFnDependencyNode(self._m_obj)

    #... Properties ...#
    @property
    def m_obj(self):
        """
        Returns the MObject associated with this object.

        Returns:
            MObject: The MObject associated with this object.
        """
        return self._m_obj
    
    @property
    def dependnode_fn(self):
        """
        Returns the MFnDependencyNode object associated with this object.

        Returns:
            om.MFnDependencyNode: The MFnDependencyNode object.
        """
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

        if not self._m_obj.hasFn(om.MFn.kDagNode):
            raise ValueError(f'{node} is a not a DAG node. Please use the DependencyNodeData class instead.')

        self._dag_path = self._get_dag_path()
        self._transform_fn = self._get_transform_fn()
        self._shapes = self._get_shapes()
        self._shapes_fn = self._get_shapes_fn()
        self._vtx_component = self._get_vtx_component()
        self._vtx_ids = self._get_vtx_ids()
        self._vtx_counts = self._get_vtx_counts()

    #... Private methods ...#
    def _get_dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.
        """
        return om.MDagPath.getAPathTo(self._m_obj)

    def _get_transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        return om.MFnTransform(self._dag_path) if self._dag_path.apiType() == om.MFn.kTransform else None

    def _get_shapes(self):
        """
        Returns a list of shape nodes attached to the object.

        Returns:
            list: A list of shape nodes attached to the object.

        Raises:
            ValueError: If the object has no shape node.
        """
        return [
            om.MFnDagNode(self._dag_path.child(i)).getPath()
            for i in range(self._dag_path.childCount())
            if self._dag_path.child(i).hasFn(om.MFn.kShape) and not om.MFnDagNode(self._dag_path.child(i)).isIntermediateObject
        ]

    def _get_shapes_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        shapes_fn = []
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
                shapes_fn.append(fn_set)

            return shapes_fn
        else:
            return None

    def _get_vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        vtx_components = []
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

                vtx_components.append(vtx_component)

            return vtx_components
        
    def _get_vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        vtx_ids = []
        
        if self.shapes_fn:
            for shape_fn in self._shapes_fn:
                if shape_fn.type() == om.MFn.kMesh:
                    vtx_id = range(0, len(cmds.ls('{}.vtx[*]'.format(self.dependnode_fn.name()), fl=True)))
                else:
                    vtx_id = range(0, len(cmds.ls('{}.cv[*]'.format(self.dependnode_fn.name()), fl=True)))

                vtx_ids.append(vtx_id)

            return vtx_ids
        else:
            return None
        
    def _get_vtx_counts(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
        return [len(vtx_id) for vtx_id in self._vtx_ids]

    #... Properties ...#
    @property
    def dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.
        """
        return self._dag_path
        
    @property
    def shapes(self):
        """
        Retrieves the shape node for the node.

        Returns:
            List[om.MObject]: List of shape nodes for the node.
        """
        return self._shapes

    @property
    def transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        return self._transform_fn
    
    @property
    def shapes_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        return self._shapes_fn

    @property
    def vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        return self._vtx_component
    
    @property
    def vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        return self._vtx_ids
    
    @property
    def vtx_counts(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
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
        self._name = name
        self.data = data

        self.meta_node = cmds.createNode('network', name=f'{self._name}_metaData')

        self._create_attrs()

    #... Public methods ...#
    @classmethod
    def rebuild(cls, meta_node):
        """
        Rebuilds a MetaNode instance from a serialized meta node.

        Args:
            meta_node (str): The name of the serialized meta node.

        Returns:
            MetaNode: The rebuilt MetaNode instance.
        """
        deserialize_meta_node = DeserializeMetaNode(meta_node=meta_node)

        return deserialize_meta_node.rebuild()

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

    Attributes:
        ATTR_SKIPTS (list): A list of attribute names to skip during serialization.

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

    ATTR_SKIPTS = ['message','caching','frozen','isHistoricallyInteresting',
                    'nodeState','binMembership','affects','affectedBy']

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

    #... Public methods ...#
    def rebuild(self):
        """
        Rebuilds the class instance from the serialized data.

        Returns:
            The rebuilt class instance.
        """
        class_instance = self._class.from_data(self.meta_node, self.data)
            
        return class_instance

    #... Private methods ...#
    def _deseriazlie_data(self):
        """
        Deserializes the data from the meta node.
        """
        attrs_mobj = [self.meta_node.dependnode_fn.attribute(attr) for attr in cmds.listAttr(self.meta_node.dependnode_fn.absoluteName())\
                if attr not in self.ATTR_SKIPTS]
        attrs_fn = [attr.apiTypeStr for attr in attrs_mobj]
        
        for attr, attr_fn in zip(attrs_mobj, attrs_fn):
            attr_name = self._get_attribute_name(attr)

            if attr_fn == 'kMessageAttribute':
                self._data[attr_name] = self._deserialize_message_attr(attr)
            if attr_fn == 'kTypedAttribute':
                self._data[attr_name] = self._deserialize_typed_attr(attr)
            if attr_fn == 'kNumericAttribute':
                self._data[attr_name] = self._deserialize_numeric_attr(attr)

    def _get_attribute_name(self, attr):
        """
        Gets the attribute name from the given attribute.

        Args:
            attr: The attribute.

        Returns:
            The attribute name.
        """
        return self.meta_node.dependnode_fn.findPlug(attr, True).partialName()
    
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

        connected_node = DagNodeData(om.MFnDagNode(connected_node).fullPathName())

        return connected_node.dag_path

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
