""" ********************************************************************
content      = This module contains a class for exporting/importing skincluster data

version      = 1.0.2
date         = 2023-05-15

how to       = skincluster.NodeData(obj), skincluster.SkinclusterData(obj)
dependencies = json

author       = Einar Mar Magnusson (einarmarmagnuss@gmail.com)
******************************************************************** """
import os

import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds

import json

class NodeData(object):
    """ Stores basic node data """
    def __init__(self, node=None):
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

    # ======================================================================
    def __get_mobj(self):
        return om.MGlobal.getSelectionListByName(self.node).getDependNode(0)

    def __get_dag_path(self):
        return om.MGlobal.getSelectionListByName(self.node).getDagPath(0)

    def __get_shape(self):
        shape = None

        try:
            shape = om.MGlobal.getSelectionListByName(self.node).getDagPath(0).extendToShape()
        except:
            shape = None

        return shape

    def __get_transform_fn(self):
        fn_set = None

        if self.dag_path.apiType() == om.MFn.kTransform:
            fn_set = om.MFnTransform(self.dag_path)

        return fn_set

    def __get_shape_fn(self):
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
        vtx_ids = None

        if self.shape:
            if self.shape.apiType() == om.MFn.kMesh:
                vtx_ids = range(0, len(cmds.ls('{}.vtx[*]'.format(self.node), fl=True)))
            else:
                vtx_ids = range(0, len(cmds.ls('{}.cv[*]'.format(self.node), fl=True)))

        return vtx_ids

    def __get_vtx_count(self):
        vtx_count = None

        if self.vtx_ids:
            vtx_count = len(self.vtx_ids)

        return vtx_count


class SkinclusterData(NodeData):
    """ Stores skincluster data from node. Needs NodeData class as parent. """
    def __init__(self, node=None, skinclusterNode=None):
        super(SkinclusterData, self).__init__(node)

        self.skinclusterNode = skinclusterNode

        self.skinclusterName = 'skinCluster_{}'.format(self.node)

        # --- Skincluster data
        self.skincluster         = self.__getSkincluster()
        self.skinclusterFn       = self.__getSkinclusterFn()
        self.influenceNames      = self.__getSkinclusterInfluenceNames()
        self.influenceIndices    = self.__getSkinclusterInfluenceIndices()
        self.bindPreMatrixValues = self.__getBindPreMatrixValues()
        self.bindPreMatrixInputs = self.__getBindPreMatrixInputs()

        # --- Skincluster weights data
        self.weights      = self.__getSkinclusterWeights()
        self.blendWeights = self.__getSkinclusterBlendWeights()

        # --- Skincluster settings data
        self.envelope          = self.__getSkinclusterAttrValue(attr='envelope')
        self.skinningMethod    = self.__getSkinclusterAttrValue(attr='skinningMethod')
        self.useComponents     = self.__getSkinclusterAttrValue(attr='useComponents')
        self.normalizeWeights  = self.__getSkinclusterAttrValue(attr='normalizeWeights')
        self.deformUserNormals = self.__getSkinclusterAttrValue(attr='deformUserNormals')

        return

    # ======================================================================
    def __getSkincluster(self):

        if self.skinclusterNode:
            skincls = self.skinclusterNode
        else:
            skincls = None

            if self.shape:
                try:
                    skincls = cmds.ls(cmds.listHistory(self.dag_path.fullPathName()),
                                      type='skinCluster')[0]
                except:
                    raise TypeError('{} does not have a skincluster node!'.format(self.shape))

                    return

            else:
                raise TypeError('{} does not have a shape node!'
                                .format(self.dag_path.partialPathName()))

                return

        return skincls

    def __getSkinclusterFn(self):
        skincluster_mobj = om.MGlobal.getSelectionListByName(self.skincluster).getDependNode(0)
        skincls_fn = oma.MFnSkinCluster(skincluster_mobj)

        return skincls_fn

    def __getSkinclusterInfluenceNames(self):
        influenceNames = [infl.partialPathName() for infl in self.skinclusterFn.influenceObjects()]

        return influenceNames

    def __getSkinclusterInfluenceIndices(self):
        mObjInfluences = self.skinclusterFn.influenceObjects()

        influences = om.MIntArray()
        for influence in range(len(mObjInfluences)):
            influences.append(influence)

        return influences

    def __getSkinclusterAttrValue(self, attr):
        attr_value = cmds.getAttr('{}.{}'.format(self.skincluster, attr))

        return attr_value

    def __getSkinclusterWeights(self):
        weights, _ = self.skinclusterFn.getWeights(self.shape, self.vtx_component)

        return weights

    def __getSkinclusterBlendWeights(self):
        blendWeights = self.skinclusterFn.getBlendWeights(self.shape, self.vtx_component)

        return blendWeights

    def __getBindPreMatrixValues(self):
        bindPreMatrixValues = [cmds.getAttr('{}.bindPreMatrix[{}]'.format(self.skincluster, i)) for i in self.influenceIndices]

        return bindPreMatrixValues

    def __getBindPreMatrixInputs(self):
        bindPreMatrixInputs = cmds.listConnections('{}.bindPreMatrix'.format(self.skincluster),
                                                   source=True, destination=False) or []

        return bindPreMatrixInputs


def saveSkinclusterData(node, path):

    if not os.path.exists('{}/skincluster'.format(path)):
        os.makedirs('{}/skincluster'.format(path))

    fullPath = '{}/skincluster/{}.json'.format(path, node)

    cSkinclusterData = SkinclusterData(node)

    data = {'skincluster': cSkinclusterData.skincluster,
            'skinclusterName': cSkinclusterData.skinclusterName,
            'influenceNames': cSkinclusterData.influenceNames,
            'influenceIndices': list(cSkinclusterData.influenceIndices),
            'bindPreMatrixValues': cSkinclusterData.bindPreMatrixValues,
            'bindPreMatrixInputs': cSkinclusterData.bindPreMatrixInputs,
            'weights': list(cSkinclusterData.weights),
            'blendWeights': list(cSkinclusterData.blendWeights),
            'envelope': cSkinclusterData.envelope,
            'skinningMethod': cSkinclusterData.skinningMethod,
            'useComponents': cSkinclusterData.useComponents,
            'normalizeWeights': cSkinclusterData.normalizeWeights,
            'deformUserNormals': cSkinclusterData.deformUserNormals}

    fileobj = open(fullPath, mode='w')
    json.dump(data, fileobj)
    fileobj.close()

    return

def loadSkinclusterData(node, path):

    fullPath = os.path.join(path, '{}.json'.format(node))

    fileobj = open(fullPath, mode='rb')
    fileobjStr = fileobj.read()
    data = json.loads(fileobjStr)
    fileobj.close()

    for joint in data['influenceNames']:
        if not cmds.objExists(joint):
            cmds.createNode('joint', name=joint, skipSelect=True)

    if data.get('bindPreMatrixInputs'):
        for joint in data['bindPreMatrixInputs']:
            if not cmds.objExists(joint):
                cmds.createNode('joint', name=joint, skipSelect=True)

    cmds.skinCluster(data['influenceNames'], node, name=data['skinclusterName'], tsb=True)

    # if data.get('bindPreMatrixValues'):
    #     for i, value in enumerate(data['bindPreMatrixValues']):
    #         cmds.setAttr('{}.bindPreMatrix[{}]'.format(data['skinclusterName'], i), value, type='matrix')
    #
    # if data.get('bindPreMatrixInputs'):
    #     for i, infl in zip(data['influenceIndices'], data['bindPreMatrixInputs']):
    #         cmds.connectAttr('{}.worldInverseMatrix'.format(infl),
    #                          '{}.bindPreMatrix[{}]'.format(data['skinclusterName'], i))

    cSkinclusterData = SkinclusterData(node)

    cmds.setAttr('{}.envelope'.format(data['skinclusterName']), data['envelope'])
    cmds.setAttr('{}.skinningMethod'.format(data['skinclusterName']), data['skinningMethod'])
    cmds.setAttr('{}.useComponents'.format(data['skinclusterName']), data['useComponents'])
    cmds.setAttr('{}.normalizeWeights'.format(data['skinclusterName']), data['normalizeWeights'])
    cmds.setAttr('{}.deformUserNormals'.format(data['skinclusterName']), data['deformUserNormals'])

    cSkinclusterData.skinclusterFn.setWeights(cSkinclusterData.shape,
                                              cSkinclusterData.vtx_component,
                                              om.MIntArray(data['influenceIndices']),
                                              om.MDoubleArray(data['weights']),
                                              True,
                                              False)

    cSkinclusterData.skinclusterFn.setBlendWeights(cSkinclusterData.shape,
                                                   cSkinclusterData.vtx_component,
                                                   om.MDoubleArray(data['blendWeights']))

    cmds.skinPercent(data['skinclusterName'], cmds.listRelatives(node, shapes=True, noIntermediate=True)[0],
                     normalize=True)

    return

def stackSkincluster(source, target):

    cSourceSkincluster = SkinclusterData(source)

    skincluster = cmds.deformer(target, type='skinCluster', name='MERGED__{}'.format(cSourceSkincluster.skinclusterName))[0]

    for i, infl, matrixValue in zip(cSourceSkincluster.influenceIndices, cSourceSkincluster.influenceNames,
                                    cSourceSkincluster.bindPreMatrixValues):

        cmds.setAttr('{}.bindPreMatrix[{}]'.format(skincluster, i), matrixValue, type='matrix')

        cmds.connectAttr('{}.worldMatrix[0]'.format(infl),
                         '{}.matrix[{}]'.format(skincluster, i))

    for i, delta in enumerate(cSourceSkincluster.bindPreMatrixInputs):
        cmds.connectAttr('{}.worldInverseMatrix[0]'.format(delta),
                         '{}.bindPreMatrix[{}]'.format(skincluster, i))

    cTargetSkincluster = SkinclusterData(target, skincluster)

    cTargetSkincluster.skinclusterFn.setWeights(cTargetSkincluster.shape,
                                                cTargetSkincluster.vtx_component,
                                                cTargetSkincluster.influenceIndices,
                                                cSourceSkincluster.weights,
                                                True,
                                                False)

    cTargetSkincluster.skinclusterFn.setBlendWeights(cTargetSkincluster.shape,
                                                     cTargetSkincluster.vtx_component,
                                                     cSourceSkincluster.blendWeights)

def copySkincluster(source, target):

    cSourceSkincluster = SkinclusterData(source)

    try:
        skincluster = cmds.ls(cmds.listHistory(target), type='skinCluster')[0]
    except:
        skincluster = cmds.skinCluster(cSourceSkincluster.influenceNames, target, tsb=True,
                                       name='skinCluster_{}'.format(target))[0]

    cmds.copySkinWeights(sourceSkin=cSourceSkincluster.skincluster,
                         destinationSkin=skincluster,
                         noMirror=True,
                         normalize=True,
                         surfaceAssociation="closestPoint",
                         influenceAssociation="name")


