"""
This module contains the NodeData class for storing basic node data.
"""

import maya.api.OpenMaya as om

class NodeData(object):
    """
    Represents data associated with a node in Maya.

    Attributes:
        node (str): The name of the node.
        mobj (om.MObject): The MObject for the node.
        dag_path (om.MDagPath): The MDagPath for the node.
        shape (om.MDagPath): The shape node for the node.
        transform_fn (om.MFnTransform): The MFnTransform for the node.
        shape_fn (om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface): The function set for the shape node.
        vtx_component (om.MObject): The vertex component for the shape node.
        vtx_ids (list): The vertex IDs for the shape node.
        vtx_count (int): The vertex count for the shape node.
    """

    def __init__(self, node=None):
        """
        Initializes a new instance of the NodeData class.

        Args:
            node (str): The name of the node.

        Raises:
            TypeError: If no node is assigned.
        """
        super(NodeData, self).__init__()

        if not node:
            raise TypeError('No node assigned')

        self.node = node

        # --- Object data
        self.mobj          = self.__get_mobj()
        self.dag_path      = self.__get_dag_path()

        # --- Shape data
        self.shape         = self.__get_shape()
        # self.shapeComponent = self.__getShapeComponent()

        # --- Function set data
        self.transform_fn  = self.__get_transform_fn()
        self.shape_fn      = self.__get_shape_fn()

        # --- Vtx data
        self.vtx_component = self.__get_vtx_component()
        self.vtx_ids       = self.__get_vtx_ids()
        self.vtx_count     = self.__get_vtx_count()

        return

    def __get_mobj(self):
        """
        Retrieves the MObject for the node.

        Returns:
            om.MObject: The MObject for the node.
        """
        return om.MGlobal.getSelectionListByName(self.node).getDependNode(0)

    def __get_dag_path(self):
        """
        Retrieves the MDagPath for the node.

        Returns:
            om.MDagPath: The MDagPath for the node.
        """
        return om.MGlobal.getSelectionListByName(self.node).getDagPath(0)

    def __get_shape(self):
        """
        Retrieves the shape node for the node.

        Returns:
            om.MDagPath: The shape node for the node.
        """
        shape = None

        try:
            shape = om.MGlobal.getSelectionListByName(self.node).getDagPath(0).extendToShape()
        except:
            shape = None

        return shape

    def __get_transform_fn(self):
        """
        Retrieves the MFnTransform for the node.

        Returns:
            om.MFnTransform: The MFnTransform for the node.
        """
        fn_set = None

        if self.dag_path.apiType() == om.MFn.kTransform:
            fn_set = om.MFnTransform(self.dag_path)

        return fn_set

    def __get_shape_fn(self):
        """
        Retrieves the MFnMesh, MFnNurbsCurve, or MFnNurbsSurface for the shape node.

        Returns:
            om.MFnMesh or om.MFnNurbsCurve or om.MFnNurbsSurface: The function set for the shape node.
        """
        fn_set = None

        if self.shape:
            if self.shape.apiType() == om.MFn.kMesh:
                fn_set = om.MFnMesh(self.dag_path)

            if self.shape.apiType() == om.MFn.kNurbsCurve:
                fn_set = om.MFnNurbsCurve(self.dag_path)

            if self.shape.apiType() == om.MFn.kNurbsSurface:
                fn_set = om.MFnNurbsSurface(self.dag_path)

        return fn_set

    def __get_vtx_component(self):
        """
        Retrieves the vertex component for the shape node.

        Returns:
            om.MObject: The vertex component for the shape node.
        """
        vtx_component = None

        if self.shape:
            if self.shape.apiType() == om.MFn.kMesh:
                comp = om.MFnSingleIndexedComponent()
                vtx_component = comp.create(om.MFn.kMeshVertComponent)
                comp.setCompleteData(self.shape_fn.numVertices)

            if self.shape.apiType() == om.MFn.kNurbsCurve:
                comp = om.MFnSingleIndexedComponent()
                vtx_component = comp.create(om.MFn.kCurveCVComponent)
                comp.setCompleteData(self.shape_fn.numCVs)

            if self.shape.apiType() == om.MFn.kNurbsSurface:
                comp = om.MFnDoubleIndexedComponent()
                vtx_component = comp.create(om.MFn.kSurfaceCVComponent)
                comp.setCompleteData(self.shape_fn.numCVsInU, self.shape_fn.numCVsInV)

        return vtx_component

    def __get_vtx_ids(self):
        """
        Retrieves the vertex IDs for the shape node.

        Returns:
            list: The vertex IDs for the shape node.
        """
        vtx_ids = None

        if self.shape:
            if self.shape.apiType() == om.MFn.kMesh:
                vtx_ids = range(0, len(cmds.ls('{}.vtx[*]'.format(self.node), fl=True)))
            else:
                vtx_ids = range(0, len(cmds.ls('{}.cv[*]'.format(self.node), fl=True)))

        return vtx_ids

    def __get_vtx_count(self):
        """
        Retrieves the vertex count for the shape node.

        Returns:
            int: The vertex count for the shape node.
        """
        vtx_count = None

        if self.vtx_ids:
            vtx_count = len(self.vtx_ids)

        return vtx_count


