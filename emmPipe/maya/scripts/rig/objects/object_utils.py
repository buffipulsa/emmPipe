
import maya.api.OpenMaya as om

from rig.objects.object_data import DependencyNodeData

def transfer_connections(from_node, to_node):
    """
    Transfers connections from one node to another.

    Args:
        from_node (DagNodeData): The source node from which connections will be transferred.
        to_node (DagNodeData): The destination node to which connections will be transferred.
    
    Returns:
        None
    """
    dg_mod = om.MDGModifier()

    for plug in from_node.dependnode_fn.getConnections():
        for src_plug in plug.connectedTo(True, False):
            for plug in src_plug.connectedTo(False,True):
                to_plug = to_node.dependnode_fn.findPlug(plug.attribute(), False)
                dg_mod.disconnect(src_plug, plug)
                dg_mod.connect(src_plug, to_plug)

        for dest_plug in plug.connectedTo(False, True):
            for plug in dest_plug.connectedTo(True, False):
                to_plug = to_node.dependnode_fn.findPlug(plug.attribute(), True)
                if plug.isElement:
                    index = plug.logicalIndex()
                    to_plug = to_plug.elementByLogicalIndex(index)

                dg_mod.disconnect(plug, dest_plug)
                dg_mod.connect(to_plug, dest_plug)

    dg_mod.doIt()

    return
