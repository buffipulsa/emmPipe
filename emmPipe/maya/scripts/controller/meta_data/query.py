
import maya.api.OpenMaya as om
import maya.cmds as cmds

from rig.objects.object_data import DependencyNodeData

class MetaDataQuery:

    @classmethod
    def skeleton_base(cls):
        
        return cls.scan_scene('SkeletonBase')

    @classmethod
    def skeleton_creator(cls):
        
        return cls.scan_scene('SkeletonCreator')
    
    @classmethod
    def control(cls):

        return cls.scan_scene('Control')
    
    @staticmethod
    def scan_scene(class_type):
        
        dep_node_iter = om.MItDependencyNodes()
        
        meta_nodes = []
        while not dep_node_iter.isDone():
            node = DependencyNodeData(dep_node_iter.thisNode())
            type_name = node.dependnode_fn.typeName
            node_name = node.dependnode_fn.name()
            
            # Check if the node is a network node
            if type_name == 'network':
                if cmds.objExists(f'{node_name}.__class_name'):
                    if cmds.getAttr(f'{node_name}.__class_name') == class_type:        
                        meta_nodes.append(node_name)
                
            dep_node_iter.next()
        
        return meta_nodes