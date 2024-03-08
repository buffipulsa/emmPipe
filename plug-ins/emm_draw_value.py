""" ********************************************************************
content      = This module contains a custom locator that draws input values
               in camera.

version      = 0.0.1
date         = 2022-01-08

how to       = cmds.createNode("emmDrawValue")

author       = Einar Mar Magnusson (einarmarmagnuss@gmail.com)
******************************************************************** """

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

def maya_useNewAPI():
    pass

class emmDrawValue(omui.MPxLocatorNode):

    TYPE_NAME = 'emmDrawValue'
    TYPE_ID = om.MTypeId(0x00138580)
    DRAW_CLASSIFICATION = 'drawdb/geometry/emmDrawValue'
    DRAW_REGISTRANT_ID = 'emmDrawValue'

    value1_obj = None
    value2_obj = None

    def __init__(self):
        super(emmDrawValue, self).__init__()

    @classmethod
    def creator(cls):
        return emmDrawValue()

    @classmethod
    def initialize(cls):
        numeric_attr = om.MFnNumericAttribute()

        cls.value1_obj = numeric_attr.create('value1', 'v1', om.MFnNumericData.kDouble, 0.0)
        numeric_attr.keyable = True
        numeric_attr.readable = False

        cls.value2_obj = numeric_attr.create('value2', 'v2', om.MFnNumericData.kDouble, 0.0)
        numeric_attr.keyable = True
        numeric_attr.readable = False

        cls.addAttribute(cls.value1_obj)
        cls.addAttribute(cls.value2_obj)

    def postConstructor(self):
        # ---  Rename the locators transform and shape
        node_fn = om.MFnDependencyNode(self.thisMObject())
        node_fn.setName("emmDrawValueShape#")

class emmDrawValueUserData(om.MUserData):

    def __init__(self, deleteAfterUse=False):
        super(emmDrawValueUserData, self).__init__(deleteAfterUse)

        self.value = 0.0

class emmDrawValueDrawOverride(omr.MPxDrawOverride):

    DEFAULT_WINDOW_WIDTH = 0
    DEFAULT_SCALE_VALUE = 1

    NAME = 'DrawValueDrawOverride'

    def __init__(self, obj):
        super(emmDrawValueDrawOverride, self).__init__(obj, None, True)

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not data:
            data = emmDrawValueUserData()

        value1_obj = obj_path.node()
        node_fn = om.MFnDependencyNode(value1_obj)

        data.value1 = node_fn.findPlug('value1', False).asDouble()
        data.value2 = node_fn.findPlug('value2', False).asDouble()

        # ---  Set initial status for each input
        data.status1 = False
        data.status2 = False

        # ---  Get the connected nodes name and plug
        mPlugArray = node_fn.getConnections()

        for plug in mPlugArray:
            print plug
            if 'value1' in plug.name():
                data.status1 =True
            if 'value2' in plug.name():
                data.status2 =True

        if mPlugArray:
            if len(mPlugArray) == 1:
                connected_node1 = mPlugArray[0].connectedTo(True, False)
                connected_node1_mObj = connected_node1[0].node()

                if connected_node1_mObj.apiTypeStr == 'kUnitConversion':
                    data.connected_node1_name = self.bypassUnitConversionNode(connected_node1_mObj)
                else:
                    data.connected_node1_name = connected_node1[0].name()
            if len(mPlugArray) == 2:
                connected_node1 = mPlugArray[0].connectedTo(True, False)
                connected_node1_mObj = connected_node1[0].node()

                if connected_node1_mObj.apiTypeStr == 'kUnitConversion':
                    data.connected_node1_name = self.bypassUnitConversionNode(connected_node1_mObj)
                else:
                    data.connected_node1_name = connected_node1[0].name()

                connected_node2 = mPlugArray[1].connectedTo(True, False)
                connected_node2_mObj = connected_node2[0].node()

                if connected_node2_mObj.apiTypeStr == 'kUnitConversion':
                    data.connected_node2_name = self.bypassUnitConversionNode(connected_node2_mObj)
                else:
                    data.connected_node2_name = connected_node2[0].name()

            # ---  Get active viewport
            active_window = omui.M3dView.active3dView()

            active_window_width = active_window.portWidth()
            active_window_height = active_window.portHeight()

            if not emmDrawValueDrawOverride.DEFAULT_WINDOW_WIDTH:
                emmDrawValueDrawOverride.DEFAULT_WINDOW_WIDTH = active_window_width

            emmDrawValueDrawOverride.DEFAULT_SCALE_VALUE = float(active_window_width) \
                                                           / float(emmDrawValueDrawOverride.DEFAULT_WINDOW_WIDTH)

            if emmDrawValueDrawOverride.DEFAULT_SCALE_VALUE < 1:
                data.width_scale_value = emmDrawValueDrawOverride.DEFAULT_SCALE_VALUE
            else: data.width_scale_value = 1

            print data.width_scale_value
            print emmDrawValueDrawOverride.DEFAULT_WINDOW_WIDTH
            print active_window_width

            data.active_window_width = active_window_width * 0.8
            data.active_window_height = active_window_height * 0.9

        return data

    def bypassUnitConversionNode(self, mObj):

        node_fn = om.MFnDependencyNode(mObj)
        mPlugArray = node_fn.getConnections()
        connected_node = mPlugArray[0].connectedTo(True, False)

        return connected_node[0].name()


    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if data.status1:
            draw_manager.beginDrawable()

            # ---  Draw connected node
            text_color = om.MColor((1.,1.,0.))
            draw_manager.setColor(text_color)
            draw_manager.setFontName('verdana')
            draw_manager.setFontSize(int(12*data.width_scale_value))
            draw_manager.text2d(om.MPoint(data.active_window_width,data.active_window_height),
                                '{} =     '.format(data.connected_node1_name),
                                1,
                                [int(300*data.width_scale_value),40],
                                om.MColor((1.,0.,0.,0.1)),
                                False)

            # ---  Draw connected value
            value_color = om.MColor((0., 1., 0.))
            draw_manager.setColor(value_color)
            draw_manager.setFontName('verdana')
            draw_manager.text2d(om.MPoint(data.active_window_width+100, data.active_window_height),
                                str(round(data.value1, 2)),
                                0,
                                [250, 40],
                                om.MColor((1., 0., 0., 0.)),
                                False)
            draw_manager.endDrawable()

        if data.status2:
            draw_manager.beginDrawable()
            # ---  Draw connected node
            text_color = om.MColor((0.,1.,1.))
            draw_manager.setColor(text_color)
            draw_manager.setFontName('verdana')
            draw_manager.setFontSize(12)
            if data.status1:
                text_pos = om.MPoint(data.active_window_width, data.active_window_height - 50)
            else:
                text_pos = om.MPoint(data.active_window_width, data.active_window_height)
            draw_manager.text2d(text_pos,
                                '{} =     '.format(data.connected_node2_name),
                                1,
                                [300,40],
                                om.MColor((0.,1.,0.,0.1)),
                                False)

            # ---  Draw connected value
            value_color = om.MColor((1., 0., 0.))
            draw_manager.setColor(value_color)
            draw_manager.setFontName('verdana')
            if data.status1:
                text_pos = om.MPoint(data.active_window_width+100, data.active_window_height-50)
            else:
                text_pos = om.MPoint(data.active_window_width + 100, data.active_window_height)
            draw_manager.text2d(text_pos,
                                str(round(data.value2, 2)),
                                0,
                                [250, 40],
                                om.MColor((0., 0., 0., 0.)),
                                False)
            draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return emmDrawValueDrawOverride(obj)

def initializePlugin(plugin):

    vendor = 'Einar Mar Magnusson'
    version = '1.0.0'

    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerNode(emmDrawValue.TYPE_NAME,
                               emmDrawValue.TYPE_ID,
                               emmDrawValue.creator,
                               emmDrawValue.initialize,
                               om.MPxNode.kLocatorNode,
                               emmDrawValue.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError('Failed to register node: {0}'.format(emmDrawValue.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(emmDrawValue.DRAW_CLASSIFICATION,
                                                      emmDrawValue.DRAW_REGISTRANT_ID,
                                                      emmDrawValueDrawOverride.creator)
    except:
        om.MGlobal.displayError('Failed to register draw override: {0}'.format(emmDrawValueDrawOverride.NAME))

def uninitializePlugin(plugin):

    plugin_fn = om.MFnPlugin(plugin)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(emmDrawValue.DRAW_CLASSIFICATION,
                                                        emmDrawValue.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError('Failed to deregister draw override: {0}'.format(emmDrawValueDrawOverride.NAME))
    try:
        plugin_fn.deregisterNode(emmDrawValue.TYPE_ID)
    except:
        om.MGlobal.displayError('Failed to deregister node: {0}'.format(emmDrawValue.TYPE_NAME))