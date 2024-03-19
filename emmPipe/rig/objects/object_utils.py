
import maya.cmds as cmds

def node_with_attr(node, attr):

    all_nodes = cmds.ls(node, dag=True, long=True)

    for node in all_nodes:
        if cmds.attributeQuery(attr, node=node, exists=True):
            return node
    
    return None

def node_by_type(node, node_type):
    
    all_nodes = cmds.ls(node, dag=True, long=True)
    
    for node in all_nodes:
        if cmds.nodeType(node) == node_type:
            return node
    
    return None

def nodes_with_attr(attr):

    nodes = [node for node in cmds.ls(dag=True, long=True) \
             if cmds.attributeQuery(attr, node=node, exists=True)]
    
    return nodes 