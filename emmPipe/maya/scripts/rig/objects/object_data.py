
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
