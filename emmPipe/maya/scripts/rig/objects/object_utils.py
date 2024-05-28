
import maya.api.OpenMaya as om

from rig.objects.object_data import DagNodeData

def transfer_connections(from_node, to_node, exclude=[]):
    """
    Transfers connections from one node to another.

    Args:
        from_node (DagNodeData): The source node from which connections will be transferred.
        to_node (DagNodeData): The destination node to which connections will be transferred.
    
    Returns:
        None
    """
    if not isinstance(from_node, DagNodeData) or not isinstance(to_node, DagNodeData):
        try:
            from_node = DagNodeData(from_node)
            to_node = DagNodeData(to_node)
        except:
            raise ValueError("Invalid node data provided.")

    dg_mod = om.MDGModifier()

    for plug in from_node.dependnode_fn.getConnections():
        for src_plug in plug.connectedTo(True, False):
            for plug in src_plug.connectedTo(False,True):
                if plug.name().split('.')[-1] in exclude:
                    continue
                to_plug = to_node.dependnode_fn.findPlug(plug.attribute(), False)
                if not to_plug.isConnected:
                    dg_mod.disconnect(src_plug, plug)
                    dg_mod.connect(src_plug, to_plug)

        for dest_plug in plug.connectedTo(False, True):
            for plug in dest_plug.connectedTo(True, False):
                #print(plug.name())
                if plug.name().split('.')[-1] in exclude:
                    continue
                to_plug = to_node.dependnode_fn.findPlug(plug.attribute(), True)
                if plug.isElement:
                    index = plug.logicalIndex()
                    to_plug = to_plug.elementByLogicalIndex(index)

                #if not to_plug.isConnected:
                dg_mod.disconnect(plug, dest_plug)
                dg_mod.connect(to_plug, dest_plug)

    dg_mod.doIt()

    return
