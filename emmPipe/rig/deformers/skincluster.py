
import os
import json

import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds

from emmPipe.rig.objects.object_data import ObjectData

class SkinclusterData(ObjectData):
    """
    Class representing skin cluster data.
    """

    def __init__(self, node=None, skincluster_node=None):
        """
        Initialize the SkinclusterData object.

        Args:
            node (str): The name of the node.
            skincluster_node (str): The name of the skincluster node.

        Raises:
            TypeError: If no node is assigned.
        """
        super().__init__(node)

        if not node:
            raise TypeError('No node assigned')

        self._node = node
        self._skincluster_node = skincluster_node

        return
    
    def _get_skincluster_attr_value(self, attr):
        """
        Get the value of the specified attribute for the skin cluster.

        Args:
            attr (str): The name of the attribute.

        Returns:
            The value of the specified attribute for the skin cluster.
        """
        attr_value = cmds.getAttr('{}.{}'.format(self.skincluster, attr))
        return attr_value

    @property
    def node(self):
        """
        str: The name of the node.
        """
        return self._node

    @property
    def skincluster_node(self):
        """
        Get the name of the skincluster node.

        Returns:
            str: The name of the skincluster node.
        """
        return self._skincluster_node
    
    @property
    def skincluster_name(self):
        """
        Get the name of the skincluster node to be saved.

        Returns:
            str: The name of the skincluster node.
        """
        return 'skinCluster_{}'.format(self.node)

    @property
    def skincluster(self):
        """
        Returns the skincluster node associated with the shape node.

        If the skincluster node is already set, it returns the existing node.
        Otherwise, it tries to find the skincluster node by listing the history of the shape node
        and filtering for skinCluster type. If no skincluster node is found, it raises a TypeError.

        Returns:
            str: The name of the skincluster node.

        Raises:
            TypeError: If the shape node does not have a skincluster node or a shape node.
        """
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

            else:
                raise TypeError('{} does not have a shape node!'
                                .format(self.dag_path.partialPathName()))

        return skincls

    @property
    def skincluster_fn(self):
        """
        Returns the MFnSkinCluster object associated with the skin cluster.

        :return: The MFnSkinCluster object.
        """
        skincluster_mobj = om.MGlobal.getSelectionListByName(self.skincluster).getDependNode(0)
        skincls_fn = oma.MFnSkinCluster(skincluster_mobj)

        return skincls_fn

    @property
    def influence_names(self):
        """
        Returns a list of names of the influence objects in the skin cluster.

        Returns:
            list: A list of strings representing the names of the influence objects.
        """
        influence_names = [infl.partialPathName() for infl in self.skincluster_fn.influenceObjects()]

        return influence_names

    @property
    def influence_indices(self):
        """
        Returns the indices of the influences in the skin cluster.

        :return: A list of integers representing the indices of the influences.
        """
        m_obj_influences = self.skincluster_fn.influenceObjects()

        influences = om.MIntArray()
        for influence in range(len(m_obj_influences)):
            influences.append(influence)

        return influences

    @property
    def weights(self):
        """
        Returns the skin weights for the specified vertex component.

        Returns:
            list: The skin weights for the vertex component.
        """
        weights, _ = self.skincluster_fn.getWeights(self.shape, self.vtx_component)
        return weights

    @property
    def blend_weights(self):
        """
        Get the blend weights for the skin cluster.

        Returns:
            blendWeights (list): List of blend weights.
        """
        blendWeights = self.skincluster_fn.getBlendWeights(self.shape, self.vtx_component)

        return blendWeights

    @property
    def bind_pre_matrix_values(self):
        """
        Returns a list of bind pre-matrix values for each influence in the skin cluster.

        :return: List of bind pre-matrix values.
        """
        bindPrematrix_values = [cmds.getAttr('{}.bindPreMatrix[{}]'.format(self.skincluster, i)) for i in self.influence_indices]
        return bindPrematrix_values

    @property
    def bind_pre_matrix_inputs(self):
        """
        Returns a list of connections to the 'bindPreMatrix' attribute of the skin cluster node.

        :return: List of connections to the 'bindPreMatrix' attribute.
        :rtype: list
        """
        bindPreMatrixInputs = cmds.listConnections('{}.bindPreMatrix'.format(self.skincluster),
                                                   source=True, destination=False) or []

        return bindPreMatrixInputs
    
    @property
    def envelope(self):
        """
        Get the envelope value of the skin cluster.

        Returns:
            float: The envelope value.
        """
        envelope = cmds.getAttr('{}.envelope'.format(self.skincluster))
        return envelope
    
    @property
    def skinning_method(self):
        """
        Returns the skinning method used by the skin cluster.

        :return: The skinning method.
        :rtype: str
        """
        skinningMethod = cmds.getAttr('{}.skinningMethod'.format(self.skincluster))
        return skinningMethod
    
    @property
    def use_components(self):
        """
        Returns the value of the 'useComponents' attribute of the skin cluster.

        Returns:
            bool: The value of the 'useComponents' attribute.
        """
        useComponents = cmds.getAttr('{}.useComponents'.format(self.skincluster))
        return useComponents
    
    @property
    def normalize_weights(self):
        """
        Returns the value of the 'normalizeWeights' attribute of the skin cluster.

        :return: The value of the 'normalizeWeights' attribute.
        :rtype: bool
        """
        normalizeWeights = cmds.getAttr('{}.normalizeWeights'.format(self.skincluster))
        return normalizeWeights
    
    @property
    def deform_user_normals(self):
        """
        Returns the value of the 'deformUserNormals' attribute of the skin cluster.

        :return: The value of the 'deformUserNormals' attribute.
        :rtype: bool
        """
        deformUserNormals = cmds.getAttr('{}.deformUserNormals'.format(self.skincluster))
        return deformUserNormals


def save_skincluster_data(node, path):
    """
    Save skincluster data to a JSON file.

    Args:
        node (str): The name of the skincluster node.
        path (str): The path where the JSON file will be saved.

    Returns:
        None
    """
    if not os.path.exists('{}/skincluster'.format(path)):
        os.makedirs('{}/skincluster'.format(path))

    full_path = '{}/skincluster/{}.json'.format(path, node)

    c_skincluster_data = SkinclusterData(node)

    data = {'skincluster': c_skincluster_data.skincluster,
            'skincluster_name': c_skincluster_data.skincluster_name,
            'influence_names': c_skincluster_data.influence_names,
            'influence_indices': list(c_skincluster_data.influence_indices),
            'bind_pre_matrix_values': c_skincluster_data.bind_pre_matrix_values,
            'bind_pre_matrix_inputs': c_skincluster_data.bind_pre_matrix_inputs,
            'weights': list(c_skincluster_data.weights),
            'blend_weights': list(c_skincluster_data.blend_weights),
            'envelope': c_skincluster_data.envelope,
            'skinning_method': c_skincluster_data.skinning_method,
            'use_components': c_skincluster_data.use_components,
            'normalize_weights': c_skincluster_data.normalize_weights,
            'deform_user_normals': c_skincluster_data.deform_user_normals}

    file_obj = open(full_path, mode='w')
    json.dump(data, file_obj)
    file_obj.close()

    return

def load_skincluster_data(node, path):
    """
    Load skin cluster data from a JSON file and apply it to the specified node.

    Args:
        node (str): The name of the node to apply the skin cluster data to.
        path (str): The path to the directory containing the JSON file.

    Returns:
        None
    """
    full_path = os.path.join(path, '{}.json'.format(node))

    file_obj = open(full_path, mode='rb')
    file_obj_str = file_obj.read()
    data = json.loads(file_obj_str)
    file_obj.close()

    for joint in data['influenceNames']:
        if not cmds.objExists(joint):
            cmds.createNode('joint', name=joint, skipSelect=True)

    if data.get('bindPreMatrixInputs'):
        for joint in data['bindPreMatrixInputs']:
            if not cmds.objExists(joint):
                cmds.createNode('joint', name=joint, skipSelect=True)

    cmds.skinCluster(data['influenceNames'], node, name=data['skinclusterName'], tsb=True)

    c_skincluster_data = SkinclusterData(node)

    cmds.setAttr('{}.envelope'.format(data['skinclusterName']), data['envelope'])
    cmds.setAttr('{}.skinningMethod'.format(data['skinclusterName']), data['skinningMethod'])
    cmds.setAttr('{}.useComponents'.format(data['skinclusterName']), data['useComponents'])
    cmds.setAttr('{}.normalizeWeights'.format(data['skinclusterName']), data['normalizeWeights'])
    cmds.setAttr('{}.deformUserNormals'.format(data['skinclusterName']), data['deformUserNormals'])

    c_skincluster_data.skinclusterFn.setWeights(c_skincluster_data.shape,
                                                c_skincluster_data.vtx_component,
                                                om.MIntArray(data['influenceIndices']),
                                                om.MDoubleArray(data['weights']),
                                                True,
                                                False)

    c_skincluster_data.skinclusterFn.setBlendWeights(c_skincluster_data.shape,
                                                     c_skincluster_data.vtx_component,
                                                     om.MDoubleArray(data['blendWeights']))

    cmds.skinPercent(data['skinclusterName'], cmds.listRelatives(node, shapes=True, noIntermediate=True)[0],
                     normalize=True)

    return

def stack_skinclusters(source, target):
    """
    Stack skin clusters from the source geometry onto the target geometry.

    Args:
        source (str): The name of the source geometry.
        target (str): The name of the target geometry.

    Returns:
        None
    """
    c_source_skincluster = SkinclusterData(source)

    skincluster = cmds.deformer(target, type='skinCluster', name='MERGED__{}'.format(c_source_skincluster.skincluster_name))[0]

    for i, infl, matrix_value in zip(c_source_skincluster.influence_indices, c_source_skincluster.influence_names,
                                    c_source_skincluster.bind_pre_matrix_values):

        cmds.setAttr('{}.bindPreMatrix[{}]'.format(skincluster, i), matrix_value, type='matrix')

        cmds.connectAttr('{}.worldMatrix[0]'.format(infl),
                         '{}.matrix[{}]'.format(skincluster, i))

    for i, delta in enumerate(c_source_skincluster.bind_pre_matrix_inputs):
        cmds.connectAttr('{}.worldInverseMatrix[0]'.format(delta),
                         '{}.bindPreMatrix[{}]'.format(skincluster, i))

    c_target_skincluster = SkinclusterData(target, skincluster)

    c_target_skincluster.skincluster_fn.setWeights(c_target_skincluster.shape,
                                                c_target_skincluster.vtx_component,
                                                c_target_skincluster.influence_indices,
                                                c_source_skincluster.weights,
                                                True,
                                                False)

    c_target_skincluster.skincluster_fn.setBlendWeights(c_target_skincluster.shape,
                                                     c_target_skincluster.vtx_component,
                                                     c_source_skincluster.blend_weights)

def copySkincluster(source, target):
    """
    Copies the skin weights from the source object to the target object.

    Args:
        source (str): The name of the source object.
        target (str): The name of the target object.

    Returns:
        None
    """
    c_source_skincluster = SkinclusterData(source)

    try:
        skincluster = cmds.ls(cmds.listHistory(target), type='skinCluster')[0]
    except:
        skincluster = cmds.skinCluster(c_source_skincluster.influenceNames, target, tsb=True,
                                       name='skinCluster_{}'.format(target))[0]

    cmds.copySkinWeights(sourceSkin=c_source_skincluster.skincluster,
                         destinationSkin=skincluster,
                         noMirror=True,
                         normalize=True,
                         surfaceAssociation="closestPoint",
                         influenceAssociation="name")


