
import maya.cmds as cmds
import maya.api.OpenMaya as om

from dev.utils import convert_list_to_str, convert_str_to_list

from rig.objects.object_data import DependencyNodeData

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
    
class MetaNode:

    def __init__(self, name, data) -> None:

        self._name = name
        self.data = data

        self.meta_node = cmds.createNode('network', name=f'{self._name}_metaData')

        self._create_attrs()

    def _create_attrs(self):

        node_data = DependencyNodeData(self.meta_node)

        type_to_attr_fn = {
                str: [om.MFnTypedAttribute, om.MFnData.kString, 'setString'],
                int: [om.MFnNumericAttribute, om.MFnNumericData.kInt, 'setInt'],
                float: [om.MFnNumericAttribute, om.MFnNumericData.kFloat, 'setFloat'],
                }

        for attr_name, data in self.data.items():
            if type(data) in type_to_attr_fn:
                attr_fn, data_fn, plug_function = type_to_attr_fn[type(data)]
                
                attr_mobj = attr_fn().create(attr_name, attr_name, data_fn)

                node_data.dependnode_fn.addAttribute(attr_mobj)

                set_attr_function = getattr(node_data.dependnode_fn.findPlug(attr_name, True), plug_function)
                set_attr_function(data)

                cmds.setAttr(f'{self.meta_node}.{attr_name}', lock=True)

            else:
                if type(data) == list:
                    compound_attr = om.MFnCompoundAttribute()
                    compound_attr_mobj = compound_attr.create(attr_name, attr_name)
                    
                    for i, item in enumerate(data):
                        message_attr_mobj = om.MFnMessageAttribute().create(f'{attr_name}_{i}', f'{attr_name}_{i}')
                        compound_attr.addChild(message_attr_mobj)
                        
                        # cmds.connectAttr(f'{item.fullPathName()}.message', f'{self.meta_node}.{attr_name}.{attr_name}_{i}')

                    node_data.dependnode_fn.addAttribute(compound_attr_mobj)

                    for i, item in enumerate(data):
                        cmds.connectAttr(f'{item.fullPathName()}.message', f'{self.meta_node}.{attr_name}_{i}')

                else:
                    message_attr_mobj = om.MFnMessageAttribute().create(attr_name, attr_name)
                    node_data.dependnode_fn.addAttribute(message_attr_mobj)

                    cmds.connectAttr(f'{data.fullPathName()}.message', f'{self.meta_node}.{attr_name}')

    @property
    def name(self):
        return self.meta_node

