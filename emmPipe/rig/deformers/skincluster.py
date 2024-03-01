

import os
import json

import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds

from emmPipe.rig.objects.object_data import NodeData

class SkinclusterData(NodeData):
    """ Stores skincluster data from node. Needs NodeData class as parent. """
    def __init__(self, node=None, skincluster_node=None):
        super(SkinclusterData, self).__init__(node)

        self.skincluster_node = skincluster_node

        self.skincluster_name = 'skinCluster_{}'.format(self.node)

        # --- Skincluster data
        self.skincluster         = self._get_skincluster()
        self.skincluster_fn      = self._get_skincluster_fn()
        self.influence_names     = self._get_skincluster_influence_names()
        self.influence_indices   = self._get_skincluster_influence_indices()
        self.bind_pre_matrix_values = self._get_bind_pre_matrix_values()
        self.bind_pre_matrix_inputs = self._get_bind_pre_matrix_inputs()

        # --- Skincluster weights data
        self.weights      = self._get_skincluster_weights()
        self.blend_weights = self._get_skincluster_blend_weights()

        # --- Skincluster settings data
        self.envelope          = self._get_skincluster_attr_value(attr='envelope')
        self.skinning_method   = self._get_skincluster_attr_value(attr='skinningMethod')
        self.use_components    = self._get_skincluster_attr_value(attr='useComponents')
        self.normalize_weights = self._get_skincluster_attr_value(attr='normalizeWeights')
        self.deform_user_normals = self._get_skincluster_attr_value(attr='deformUserNormals')

        return


    def _get_skincluster(self):

        if self.skincluster_node:
            skincls = self.skincluster_node
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

    def _get_skincluster_fn(self):
        skincluster_mobj = om.MGlobal.getSelectionListByName(self.skincluster).getDependNode(0)
        skincls_fn = oma.MFnSkinCluster(skincluster_mobj)

        return skincls_fn

    def _get_skincluster_influence_names(self):
        influence_names = [infl.partialPathName() for infl in self.skincluster_fn.influenceObjects()]

        return influence_names

    def _get_skincluster_influence_indices(self):
        m_obj_influences = self.skincluster_fn.influenceObjects()

        influences = om.MIntArray()
        for influence in range(len(m_obj_influences)):
            influences.append(influence)

        return influences

    def _get_skincluster_attr_value(self, attr):
        attr_value = cmds.getAttr('{}.{}'.format(self.skincluster, attr))

        return attr_value

    def _get_skincluster_weights(self):
        weights, _ = self.skincluster_fn.getWeights(self.shape, self.vtx_component)

        return weights

    def _get_skincluster_blend_weights(self):
        blendWeights = self.skincluster_fn.getBlendWeights(self.shape, self.vtx_component)

        return blendWeights

    def _get_bind_pre_matrix_values(self):
        bindPreMatrixValues = [cmds.getAttr('{}.bindPreMatrix[{}]'.format(self.skincluster, i)) for i in self.influence_indices]

        return bindPreMatrixValues

    def _get_bind_pre_matrix_inputs(self):
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


