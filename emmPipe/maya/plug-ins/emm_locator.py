""" ********************************************************************
content      = This module contains a custom locator node class

version      = 0.0.1
date         = 2022-01-08

how to       = cmds.createNode("emmlocator", name='InsertNameHereShape')

author       = Einar Mar Magnusson (einarmarmagnuss@gmail.com)
******************************************************************** """

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

def maya_useNewAPI():
    pass


class EmmLocatorNode(omui.MPxLocatorNode):
    TYPE_NAME = "emmlocator"
    TYPE_ID = om.MTypeId(0x00138581)
    DRAW_CLASSIFICATION = "drawdb/geometry/emmlocator"
    DRAW_REGISTRANT_ID = "EmmLocatorNode"

    shape_index_obj = None

    def __init__(self):
        super(EmmLocatorNode, self).__init__()

    @classmethod
    def creator(cls):
        return EmmLocatorNode()

    def postConstructor(self):
        # ---  Rename the locators transform and shape
        node_fn = om.MFnDependencyNode(self.thisMObject())
        node_fn.setName('emmLocatorShape#')

    @classmethod
    def initialize(cls):

        numeric_attr = om.MFnNumericAttribute()
        enum_attr    = om.MFnEnumAttribute()

        SHAPE_NAMES = ('Circle', 'Square', 'Triangle', 'Box', 'Sphere')
        COLOR_NAMES = ('Dark Grey', 'Grey', 'Black', 'Light Grey', 'Medium Grey', 'Light Red',
                       'Dark Blue', 'Blue', 'Dark Green', 'Dark Purple', 'Pink', 'Orange',
                       'Dark Brown', 'Dark Red', 'Red', 'Green', 'Light Blue', 'White', 'Yellow',
                       'Baby Blue', 'Light Green', 'Light Pink', 'Light Orange', 'Light Yellow',
                       'Dark Green', 'Dark Orange', 'Dark Yellow', 'Toxic Green', 'Green',
                       'Dark Baby Blue', 'Silk Blue', 'Purple', 'Dark Pink')

        cls.shape_enum_obj = enum_attr.create('shape', 'shape', 0)
        for i, shape_name in enumerate(SHAPE_NAMES):
            enum_attr.addField('{} - {}'.format(i, shape_name), i)
        enum_attr.channelBox = True

        cls.color_enum_obj = enum_attr.create('color', 'color', 6)
        for i, color_name in enumerate(COLOR_NAMES):
            enum_attr.addField('{} - {}'.format(i, color_name), i)
        enum_attr.channelBox = True

        cls.scale_obj = numeric_attr.create("scale", "scale", om.MFnNumericData.kFloat, 1)
        numeric_attr.channelBox = True

        cls.line_width_obj = numeric_attr.create("lineWidth", "lineWidth",
                                                 om.MFnNumericData.kFloat, 1)
        numeric_attr.setMin(1)
        numeric_attr.setMax(3)
        numeric_attr.channelBox = True

        cls.orient_x_obj = numeric_attr.create("localOrientX", "localOrientX",
                                         om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(-360)
        numeric_attr.setMax(360)
        numeric_attr.channelBox = True

        cls.orient_y_obj = numeric_attr.create("localOrientY", "localOrientY",
                                          om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(-360)
        numeric_attr.setMax(360)
        numeric_attr.channelBox = True

        cls.orient_z_obj = numeric_attr.create("localOrientZ", "localOrientZ",
                                          om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(-360)
        numeric_attr.setMax(360)
        numeric_attr.channelBox = True

        cls.addAttribute(cls.orient_x_obj)
        cls.addAttribute(cls.orient_y_obj)
        cls.addAttribute(cls.orient_z_obj)
        cls.addAttribute(cls.shape_enum_obj)
        cls.addAttribute(cls.color_enum_obj)
        cls.addAttribute(cls.scale_obj)
        cls.addAttribute(cls.line_width_obj)

        cls.attributeAffects(cls.scale_obj, cls.localScale)
        cls.attributeAffects(cls.orient_x_obj, cls.localScale)
        cls.attributeAffects(cls.orient_y_obj, cls.localScale)
        cls.attributeAffects(cls.orient_z_obj, cls.localScale)


class EmmLocatorUserData(om.MUserData):

    def __init__(self, deleteAfterUse=False):
        super(EmmLocatorUserData, self).__init__(deleteAfterUse)

        self.shape_index = 0
        self.scale = 1
        self.line_width = 0
        self.color = 6
        self.orient = 0


# class EmmLocatorDrawOverride(omr.MPxDrawOverride):
#     NAME = "ControlLocatorDrawOverride"

#     def __init__(self, obj):
#         super(EmmLocatorDrawOverride, self).__init__(obj, None, True)

#     def supportedDrawAPIs(self):
#         return omr.MRenderer.kAllDevices

#     def hasUIDrawables(self):
#         return True

#     def isBounded(self, obj_path, camera_path):
#         return True

#     def boundingBox(self, obj_path, camera_path):
#         return om.MBoundingBox(om.MPoint(1.0, 1.0, 1.0),
#                                om.MPoint(-1.0, -1.0, -1.0))

#     def transform(self, obj_path, camera_path):
#         """ Create a new matrix for the shape by getting the transforms matrix
#             and adding a local matrix for position, orientation and scale """

#         locator_obj   = obj_path.node()
#         transform_obj = obj_path.transform()

#         node_fn = om.MFnDependencyNode(locator_obj)
#         trfm_fn = om.MFnDependencyNode(transform_obj)

#         local_tx = om.MPlug(locator_obj, EmmLocatorNode.localPositionX).asFloat()
#         local_ty = om.MPlug(locator_obj, EmmLocatorNode.localPositionY).asFloat()
#         local_tz = om.MPlug(locator_obj, EmmLocatorNode.localPositionZ).asFloat()
#         local_sx = om.MPlug(locator_obj, EmmLocatorNode.localScaleX).asFloat()
#         local_sy = om.MPlug(locator_obj, EmmLocatorNode.localScaleY).asFloat()
#         local_sz = om.MPlug(locator_obj, EmmLocatorNode.localScaleZ).asFloat()
#         scale    = node_fn.findPlug('scale', False).asFloat()
#         local_rx = node_fn.findPlug('localOrientX', False).asInt()
#         local_ry = node_fn.findPlug('localOrientY', False).asInt()
#         local_rz = node_fn.findPlug('localOrientZ', False).asInt()

#         # --- get the transform world matrix
#         trfm_mat_plug_array = om.MPlug(transform_obj, EmmLocatorNode.worldMatrix)
#         trfm_mat_plug_array.evaluateNumElements()
#         trfm_mat_plug = trfm_mat_plug_array.elementByPhysicalIndex(0)
#         trfm_mat_plug_obj = trfm_mat_plug.asMObject()
#         trfm_mat = om.MFnMatrixData(trfm_mat_plug_obj).matrix()

#         # --- Create a local matrix
#         local_matrix = om.MTransformationMatrix(om.MMatrix())

#         # --- set local position values
#         local_matrix.translateBy(om.MVector(local_tx, local_ty, local_tz),
#                                  om.MSpace.kObject)

#         # --- set local rotation values
#         radians_x = local_rx * (3.14 / 180)
#         radians_y = local_ry * (3.14 / 180)
#         radians_z = local_rz * (3.14 / 180)
#         orientation = om.MEulerRotation(radians_x, radians_y, radians_z, 0)

#         local_matrix.rotateBy(orientation, om.MSpace.kWorld)

#         # --- set local scale values
#         local_matrix.scaleBy((local_sx * scale, local_sy * scale, local_sz * scale),
#                              om.MSpace.kObject)

#         new_matrix = local_matrix.asMatrix() * trfm_mat

#         return new_matrix

#     def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
#         data = old_data
#         if not data:
#             data = EmmLocatorUserData()

#         locator_obj = obj_path.node()
#         node_fn = om.MFnDependencyNode(locator_obj)

#         data.shape_index = node_fn.findPlug("shape", False).asInt()
#         data.line_width  = node_fn.findPlug('lineWidth', False).asFloat()
#         data.color       = node_fn.findPlug('color', False).asInt()

#         data.display_status  = omr.MGeometryUtilities.displayStatus(obj_path)
#         data.wireframe_color = omr.MGeometryUtilities.wireframeColor(obj_path)

#         transform_obj = obj_path.transform()
#         msel = om.MSelectionList()
#         msel.add(transform_obj)
#         print(msel.getComponent(0))
        

#         return data

#     def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
#         draw_manager.beginDrawable()

#         draw_manager.setColor(data.wireframe_color)
#         if data.display_status == omr.MGeometryUtilities.kDormant:
#             draw_manager.setColorIndex(data.color)

#         draw_manager.setLineWidth(data.line_width)

#         if data.shape_index == 0:
#             # --- Draw a circle shape
#             draw_manager.circle(om.MPoint(0.0, 0.0, 0.0),
#                                 om.MVector(0.0, 1.0, 0.0),
#                                 1.0,
#                                 16,
#                                 False)

#         elif data.shape_index == 1:
#             # --- Draw a square shape
#             draw_manager.rect(om.MPoint(0.0, 0.0, 0.0),
#                               om.MVector(0.0, 0.0, 1.0),
#                               om.MVector(0.0, 1.0, 0.0),
#                               1.0,
#                               1.0,
#                               False)

#         elif data.shape_index == 2:
#             # --- Draw a triangle shape
#             point_array = om.MPointArray([(-1.0, 0.0, -1.0),
#                                           (0.0, 0.0, 1.0),
#                                           (1.0, 0.0, -1.0),
#                                           (-1.0, 0.0, -1.0)])
#             draw_manager.lineStrip(point_array, False)

#         elif data.shape_index == 3:
#             # --- Draw a box shape
#             draw_manager.box(om.MPoint(0.0, 0.0, 0.0),
#                              om.MVector(0.0, 0.0, 1.0),
#                              om.MVector(0.0, 1.0, 0.0),
#                              1.0,
#                              1.0,
#                              1.0,
#                              False)

#         elif data.shape_index == 4:
#             # --- Draw a sphere shape
#             draw_manager.sphere(om.MPoint(0.0, 0.0, 0.0),
#                                 data.scale,
#                                 10,
#                                 5,
#                                 False)

#         draw_manager.endDrawable()

#     @classmethod
#     def creator(cls, obj):
#         return EmmLocatorDrawOverride(obj)

class EmmLocatorDrawOverride(omr.MPxGeometryOverride):
    NAME = "ControlLocatorDrawOverride"

    def __init__(self, obj):
        super(EmmLocatorDrawOverride, self).__init__(obj)

    def supportedDrawAPIs(self):
        return omr.MRenderer.kOpenGL | omr.MRenderer.kDirectX11 | omr.MRenderer.kOpenGLCoreProfile

    def hasUIDrawables(self):
        return True

    def isBounded(self, obj_path, camera_path):
        return True

    def boundingBox(self, obj_path, camera_path):
        return om.MBoundingBox(om.MPoint(1.0, 1.0, 1.0),
                               om.MPoint(-1.0, -1.0, -1.0))

    def transform(self, obj_path, camera_path):
        """ Create a new matrix for the shape by getting the transforms matrix
            and adding a local matrix for position, orientation and scale """

        locator_obj   = obj_path.node()
        transform_obj = obj_path.transform()

        node_fn = om.MFnDependencyNode(locator_obj)
        trfm_fn = om.MFnDependencyNode(transform_obj)

        local_tx = om.MPlug(locator_obj, EmmLocatorNode.localPositionX).asFloat()
        local_ty = om.MPlug(locator_obj, EmmLocatorNode.localPositionY).asFloat()
        local_tz = om.MPlug(locator_obj, EmmLocatorNode.localPositionZ).asFloat()
        local_sx = om.MPlug(locator_obj, EmmLocatorNode.localScaleX).asFloat()
        local_sy = om.MPlug(locator_obj, EmmLocatorNode.localScaleY).asFloat()
        local_sz = om.MPlug(locator_obj, EmmLocatorNode.localScaleZ).asFloat()
        scale    = node_fn.findPlug('scale', False).asFloat()
        local_rx = node_fn.findPlug('localOrientX', False).asInt()
        local_ry = node_fn.findPlug('localOrientY', False).asInt()
        local_rz = node_fn.findPlug('localOrientZ', False).asInt()

        # --- get the transform world matrix
        trfm_mat_plug_array = om.MPlug(transform_obj, EmmLocatorNode.worldMatrix)
        trfm_mat_plug_array.evaluateNumElements()
        trfm_mat_plug = trfm_mat_plug_array.elementByPhysicalIndex(0)
        trfm_mat_plug_obj = trfm_mat_plug.asMObject()
        trfm_mat = om.MFnMatrixData(trfm_mat_plug_obj).matrix()

        # --- Create a local matrix
        local_matrix = om.MTransformationMatrix(om.MMatrix())

        # --- set local position values
        local_matrix.translateBy(om.MVector(local_tx, local_ty, local_tz),
                                 om.MSpace.kObject)

        # --- set local rotation values
        radians_x = local_rx * (3.14 / 180)
        radians_y = local_ry * (3.14 / 180)
        radians_z = local_rz * (3.14 / 180)
        orientation = om.MEulerRotation(radians_x, radians_y, radians_z, 0)

        local_matrix.rotateBy(orientation, om.MSpace.kWorld)

        # --- set local scale values
        local_matrix.scaleBy((local_sx * scale, local_sy * scale, local_sz * scale),
                             om.MSpace.kObject)

        new_matrix = local_matrix.asMatrix() * trfm_mat

        return new_matrix

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not data:
            data = EmmLocatorUserData()

        locator_obj = obj_path.node()
        node_fn = om.MFnDependencyNode(locator_obj)

        data.shape_index = node_fn.findPlug("shape", False).asInt()
        data.line_width  = node_fn.findPlug('lineWidth', False).asFloat()
        data.color       = node_fn.findPlug('color', False).asInt()

        data.display_status  = omr.MGeometryUtilities.displayStatus(obj_path)
        data.wireframe_color = omr.MGeometryUtilities.wireframeColor(obj_path)

        transform_obj = obj_path.transform()
        msel = om.MSelectionList()
        msel.add(transform_obj)
        print(msel.getComponent(0))
        

        return data

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        draw_manager.beginDrawable()

        draw_manager.setColor(data.wireframe_color)
        if data.display_status == omr.MGeometryUtilities.kDormant:
            draw_manager.setColorIndex(data.color)

        draw_manager.setLineWidth(data.line_width)

        if data.shape_index == 0:
            # --- Draw a circle shape
            draw_manager.circle(om.MPoint(0.0, 0.0, 0.0),
                                om.MVector(0.0, 1.0, 0.0),
                                1.0,
                                16,
                                False)

        elif data.shape_index == 1:
            # --- Draw a square shape
            draw_manager.rect(om.MPoint(0.0, 0.0, 0.0),
                              om.MVector(0.0, 0.0, 1.0),
                              om.MVector(0.0, 1.0, 0.0),
                              1.0,
                              1.0,
                              False)

        elif data.shape_index == 2:
            # --- Draw a triangle shape
            point_array = om.MPointArray([(-1.0, 0.0, -1.0),
                                          (0.0, 0.0, 1.0),
                                          (1.0, 0.0, -1.0),
                                          (-1.0, 0.0, -1.0)])
            draw_manager.lineStrip(point_array, False)

        elif data.shape_index == 3:
            # --- Draw a box shape
            draw_manager.box(om.MPoint(0.0, 0.0, 0.0),
                             om.MVector(0.0, 0.0, 1.0),
                             om.MVector(0.0, 1.0, 0.0),
                             1.0,
                             1.0,
                             1.0,
                             False)

        elif data.shape_index == 4:
            # --- Draw a sphere shape
            draw_manager.sphere(om.MPoint(0.0, 0.0, 0.0),
                                data.scale,
                                10,
                                5,
                                False)

        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return EmmLocatorDrawOverride(obj)

def initializePlugin(plugin):
    vendor = "Einar Mar Magnusson"
    version = "1.0.0"
    api_version = "2.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version, api_version)
    try:
        plugin_fn.registerNode(EmmLocatorNode.TYPE_NAME,
                               EmmLocatorNode.TYPE_ID,
                               EmmLocatorNode.creator,
                               EmmLocatorNode.initialize,
                               om.MPxNode.kLocatorNode,
                               EmmLocatorNode.DRAW_CLASSIFICATION)

    except:
        om.MGlobal.displayError("Failed to register node: {}".format(EmmLocatorNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(EmmLocatorNode.DRAW_CLASSIFICATION,
                                                      EmmLocatorNode.DRAW_REGISTRANT_ID,
                                                      EmmLocatorDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {}".format(EmmLocatorDrawOverride.NAME))


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(EmmLocatorNode.DRAW_CLASSIFICATION,
                                                        EmmLocatorNode.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {}".format(EmmLocatorDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(EmmLocatorNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to unregister node: {}".format(EmmLocatorNode.TYPE_NAME))

