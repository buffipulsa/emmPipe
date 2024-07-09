
import maya.api.OpenMaya as om
import maya.cmds as cmds

from rig.objects.object_data import DependencyNodeData, DagNodeData, RebuildObject

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
    
    @classmethod
    def meta_node_attrs_values(cls, meta_node):
        
        meta_node = DependencyNodeData(meta_node)
        fn_dep_node = meta_node.dependnode_fn

        data = {}

        module_grp = None
        control = False
        joint = False
        utility = False

        for i in range(fn_dep_node.attributeCount()):
            attr = fn_dep_node.attribute(i)
            plug = fn_dep_node.findPlug(attr, False)
            name = plug.partialName()

            if name.startswith('__') and plug.attribute().apiType() == om.MFn.kMessageAttribute:
                connected_plugs = [DagNodeData(om.MFnDependencyNode(connected_plug.node()).name()) for connected_plug in plug.connectedTo(True, False)]
                data[name.replace('__','')] = {'data': [connected_plug.dag_path for connected_plug in connected_plugs]}

                if name == '__module':
                    module_grp = connected_plugs[0]

                groups = cmds.listRelatives(module_grp.dag_path)
                groups.append('joints')
                groups.append('modules')

                for group in groups:
                    if cls.find_parent_group(connected_plugs[0].m_obj, group):
                        if not 'category' in data[name.replace('__','')]:
                            data[name.replace('__','')]['category'] = group.split('_')[0]
        
        return data

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
    
    @staticmethod
    def find_connected_nodes(node, attr=None):
        pass

    @staticmethod
    def find_parent_group(start_node_name, target_group_name):
        """Walk up the hierarchy to find the specified group name."""
        mobject = start_node_name
        
        if not mobject.hasFn(om.MFn.kDagNode):
            raise ValueError(f"The node '{start_node_name}' is not a DAG node.")
        
        dag_node = om.MFnDagNode(mobject)

        # Traverse up the hierarchy
        while True:
            parent_count = dag_node.parentCount()
            
            if parent_count == 0:
                break
            
            parent_obj = dag_node.parent(0)
            
            # Check if the parent is a DAG node
            if not parent_obj.hasFn(om.MFn.kDagNode):
                break
            
            parent_dag_node = om.MFnDagNode(parent_obj)
            
            # Check the parent node name
            if parent_dag_node.name() == target_group_name:
                return parent_dag_node.name()
            
            # Move up to the next parent
            dag_node = parent_dag_node

        # If the target group name is not found
        return None