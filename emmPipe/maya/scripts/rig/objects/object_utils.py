
import maya.cmds as cmds
import maya.api.OpenMaya as om


def node_with_attr(node, attr):

    return next((node for node in cmds.ls(node, dag=True, long=True) \
                 if cmds.attributeQuery(attr, node=node, exists=True)), None)
    
def node_by_type(node, node_type):
    
    return next((node for node in cmds.ls(node, dag=True, long=True) \
                 if cmds.nodeType(node) == node_type), None)
    
def nodes_with_attr(attr):

    nodes = [node for node in cmds.ls(dag=True, long=True) \
             if cmds.attributeQuery(attr, node=node, exists=True)]
    
    return nodes 

