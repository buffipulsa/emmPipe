
import maya.api.OpenMaya as om
import maya.cmds as cmds

class ObjectData:
    """
    Represents an object in the scene.
    """

    def __init__(self, node=None):
        """
        Initialize the ObjectData instance.

        Args:
            node (str): The name of the node.

        Raises:
            TypeError: If no node is assigned.
        """
        
        if not node:
            raise TypeError('No node assigned')

        self._node = node
        self.dag_node_types = ['transform', 'mesh', 'nurbsCurve', 'nurbsSurface', 'camera', 'light']
        
        self.selection = om.MSelectionList()
        self.selection.add(self._node)

        self._m_obj = self.selection.getDependNode(0)
        self._node = om.MFnDependencyNode(self._m_obj)
        
        try:
            self._m_dagpath = self.selection.getDagPath(0)
        except:
            self._m_dagpath = om.MDagPath()


    @property
    def node(self):
        """
        str: The name of the node.
        """
        if self._m_dagpath.isValid():
            return self._m_dagpath
        else:
            if not self._m_obj.isNull():
                return self._node
            return None

        return False

    @property
    def m_obj(self):
        """
        Retrieves the MObject for the node.

        Returns:
            om.MObject: The MObject for the node.
        """

        return self._m_obj

    # @property
    # def dag_path(self):
    #     """
    #     Retrieves the MDagPath for the node.

    #     Returns:
    #         om.MDagPath: The MDagPath for the node.
    #     """
    #     if self._m_dagpath.isValid():
    #         return self._m_dagpath
    #     else:
    #         print('No valid dag path found for {}'.format(self._node.name()))

    # @property
    # def shape(self):
    #     """
    #     Retrieves the shape node for the node.

    #     Returns:
    #         List[om.MObject]: List of shape nodes for the node.
    #     """
    #     shape_nodes = []

    #     for i in range(self._m_dagpath.childCount()):
    #         child_mobj = self._m_dagpath.child(i)
    #         depend_node = om.MFnDependencyNode(child_mobj)
    #         if child_mobj.hasFn(om.MFn.kShape):
    #             shape_nodes.append(depend_node.name())
    #         else:
    #             raise ValueError(f'{self._node.name()} has no shape node')

    #     return shape_nodes

    # @property
    # def transform_fn(self):
    #     """
    #     Retrieves the MFnTransform for the node.

    #     Returns:
    #         om.MFnTransform: The MFnTransform for the node.
    #     """
    #     fn_set = None

    #     if self.dag_path.apiType() == om.MFn.kTransform:
    #         fn_set = om.MFnTransform(self.dag_path)

    #     return fn_set

    # @property
    # def shape_fn(self):
    #     """
    #     Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

    #     Returns:
    #         om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
    #     """
    #     fn_set = None

    #     if self.shape:
    #         if self.shape.apiType() == om.MFn.kMesh:
    #             fn_set = om.MFnMesh(self.dag_path)

    #         if self.shape.apiType() == om.MFn.kNurbsCurve:
    #             fn_set = om.MFnNurbsCurve(self.dag_path)

    #         if self.shape.apiType() == om.MFn.kNurbsSurface:
    #             fn_set = om.MFnNurbsSurface(self.dag_path)

    #     return fn_set

    # @property
    # def vtx_component(self):
    #     """
    #     Retrieves the vertex component for the shape node.

    #     Returns:
    #         om.MObject: The vertex component for the shape node.
    #     """
    #     vtx_component = None

    #     if self.shape:
    #         if self.shape.apiType() == om.MFn.kMesh:
    #             comp = om.MFnSingleIndexedComponent()
    #             vtx_component = comp.create(om.MFn.kMeshVertComponent)
    #             comp.setCompleteData(self.shape_fn.numVertices)

    #         if self.shape.apiType() == om.MFn.kNurbsCurve:
    #             comp = om.MFnSingleIndexedComponent()
    #             vtx_component = comp.create(om.MFn.kCurveCVComponent)
    #             comp.setCompleteData(self.shape_fn.numCVs)

    #         if self.shape.apiType() == om.MFn.kNurbsSurface:
    #             comp = om.MFnDoubleIndexedComponent()
    #             vtx_component = comp.create(om.MFn.kSurfaceCVComponent)
    #             comp.setCompleteData(self.shape_fn.numCVsInU, self.shape_fn.numCVsInV)

    #     return vtx_component

    # @property
    # def vtx_ids(self):
    #     """
    #     Retrieves the vertex IDs for the shape node.

    #     Returns:
    #         list: The vertex IDs for the shape node.
    #     """
    #     vtx_ids = None

    #     if self.shape:
    #         if self.shape.apiType() == om.MFn.kMesh:
    #             vtx_ids = range(0, len(cmds.ls('{}.vtx[*]'.format(self.node), fl=True)))
    #         else:
    #             vtx_ids = range(0, len(cmds.ls('{}.cv[*]'.format(self.node), fl=True)))

    #     return vtx_ids

    # @property
    # def vtx_count(self):
    #     """
    #     Retrieves the vertex count for the shape node.

    #     Returns:
    #         int: The vertex count for the shape node.
    #     """
    #     vtx_count = None

    #     if self.vtx_ids:
    #         vtx_count = len(self.vtx_ids)

    #     return vtx_count


class DependencyNodeData(ObjectData):
    """
    Represents a dependency node in the scene.
    """

    def __init__(self, node=None):
        """
        Initialize the DependencyNodeData instance.

        Args:
            node (str): The name of the node.

        Raises:
            TypeError: If no node is assigned.
        """
        super().__init__(node=node)

        if cmds.nodeType(self._node.name()) in self.dag_node_types:
            raise ValueError(f'{self._node.name()} is a DAG node. Please use the DagNodeData class instead.')


class DagNodeData(ObjectData):
    """
    Represents a DAG node in the scene.
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

        self._node = node
        if cmds.nodeType(self.node) not in self.dag_node_types:
            raise ValueError(f'{self.node} is a not a DAG node. Please use the DependencyNodeData class instead.')

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

    
    def _get_dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.
        """
        if self.selection.getDagPath(0).isValid():
            return self.selection.getDagPath(0)
        else:
            raise ValueError('No valid dag path found for {}'.format(self._node.name()))
        
        return False
    
    @property
    def dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.
        """
        self._dag_path = self._get_dag_path()
        return self._dag_path

    def _get_shapes(self):
        """
        Returns a list of shape nodes attached to the object.

        Returns:
            list: A list of shape nodes attached to the object.

        Raises:
            ValueError: If the object has no shape node.
        """
        self._shapes.clear()

        if self._m_dagpath.childCount():
            for i in range(self._m_dagpath.childCount()):
                child_mobj = self._m_dagpath.child(i)
                if child_mobj.hasFn(om.MFn.kShape) and not om.MFnDagNode(child_mobj).isIntermediateObject:
                    self._shapes.append(child_mobj)

            return self._shapes
        else:        
            return None

        return False
    
    @property
    def shapes(self):
        """
        Retrieves the shape node for the node.

        Returns:
            List[om.MObject]: List of shape nodes for the node.
        """
        self._shapes = self._get_shapes()
        return self._shapes

    
    def _get_transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        if self._m_dagpath.apiType() == om.MFn.kTransform:
            self._transform_fn = om.MFnTransform(self._m_dagpath)

        return self._transform_fn

    @property
    def transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        self.transform_fn = self._get_transform_fn()
        return self._transform_fn

    def _get_shapes_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        self._shapes_fn.clear()

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
    
    @property
    def shapes_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        self._shapes_fn = self._get_shapes_fn()
        return self._shapes_fn

    def _get_vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        self._vtx_components.clear()

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

    @property
    def vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        self._vtx_component = self._get_vtx_component()
        return self._vtx_component

    def _get_vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        self._vtx_ids.clear()
        
        for shape_fn in self._shapes_fn:
            if shape_fn.type() == om.MFn.kMesh:
                self._vtx_id = range(0, len(cmds.ls('{}.vtx[*]'.format(self.node), fl=True)))
            else:
                self._vtx_id = range(0, len(cmds.ls('{}.cv[*]'.format(self.node), fl=True)))

            self._vtx_ids.append(self._vtx_id)

        return self._vtx_ids
    
    @property
    def vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        self._vtx_ids = self._get_vtx_ids()
        return self._vtx_ids
    
    
    def _get_vtx_counts(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
        self._vtx_counts.clear()

        for vtx_id in self._vtx_ids:
            vtx_count = len(vtx_id)

            self._vtx_counts.append(vtx_count)

        return self._vtx_counts
    
    @property
    def vtx_counts(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
        self._vtx_counts = self._get_vtx_count()
        return self._vtx_counts