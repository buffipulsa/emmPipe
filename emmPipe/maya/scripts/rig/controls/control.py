
import maya.cmds as cmds
import maya.api.OpenMaya as om

from dev.utils import convert_list_to_str, convert_str_to_list

from rig.controls.control_shapes import ControlShapes
from rig.objects.base_object import BaseObject
from rig.objects.object_data import DagNodeData


class Control(BaseObject):

    def __init__(self, side, name, shape) -> None:
        
        self._side = side
        self._name = name
        self._shape_name = shape

        self._scale = 1.0
        self._index = 0
        self._thickness = 1.0
        self._color = 'yellow'
        
        self._shapes = None
        self._ctrl = None
        self._srt_offset = None
        self._ctrl_data = None
        self._srt_offset_data = None

        self._meta_node = None

    def create(self):
        
        self._ctrl = ControlShapes(self._shape_name).create()
        self._srt_offset = cmds.createNode('transform')

        self._ctrl_data = DagNodeData(self._ctrl.name)
        self._srt_offset_data = DagNodeData(self._srt_offset)

        cmds.parent(self._ctrl_data.dag_path, self._srt_offset_data.dag_path)

        self._shapes = self._ctrl_data.shapes

        self._rename()
        
        self.data = self.create_meta_data()
        self.create_meta_node()

        if self._side   == 'l': self.color = 'blue'
        elif self._side == 'r': self.color = 'red'
        else:                   self.color = 'yellow'

        return self

    @property
    def m_obj(self):
        return self._ctrl_data.m_obj
    
    @property
    def dependnode_fn(self):
        return self._ctrl_data.dependnode_fn

    @property
    def dag_path(self):
        return self._ctrl_data.dag_path
    
    @property
    def meta_node(self):
        return self._meta_node
    
    @meta_node.setter
    def meta_node(self, value):
        self._meta_node = value

    @property
    def control(self):
        return self._ctrl_data
    
    @control.setter
    def control(self, value):
        self._ctrl_data = value

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        color_data = {'red': 13,
                      'blue': 6,
                      'yellow': 17}

        # ---  Check if color is valid
        if value in color_data:
            color = color_data[value]

            if hasattr(self, '_ctrl_data'):
                shapes = [shape.fullPathName() for shape in self._ctrl_data.shapes]
            else: 
                shapes =  [self.data[key].fullPathName() for key in self.data.keys() if key.startswith('shapes_') and key[-1].isdigit()]

            for shape in shapes:
                if not cmds.getAttr(f'{shape}.overrideEnabled'):
                    cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f'{shape}.overrideColor', color)
            
            #if hasattr(self, 'meta_node'):
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.color', lock=False)
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.color', value, type='string', lock=True)
        else:
            raise ValueError('Please provide a valid color name')
            
        self._color = value

    @property
    def thickness(self):
        return self._thickness
    
    @thickness.setter
    def thickness(self, value):
        if hasattr(self, '_ctrl_data'):
            shapes = [shape.fullPathName() for shape in self._ctrl_data.shapes]
        else: 
            shapes =  [self.data[key].fullPathName() for key in self.data.keys() if key.startswith('shapes_') and key[-1].isdigit()]
        
        [cmds.setAttr(f'{shape}.lineWidth', value) for shape in shapes]

        self._thickness = value

        if hasattr(self, 'meta_node'):
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.thickness', lock=False)
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.thickness', value, lock=True)

    def _rename(self):
    
        cmds.rename(self._ctrl_data.transform_fn.fullPathName(), f'{self._name}_{self._side}_{str(self._index).zfill(2)}_ctrl')
        cmds.rename(self._srt_offset_data.transform_fn.fullPathName(), f'{self._name}_{self._side}_{str(self._index).zfill(2)}_srtBuffer')
        [cmds.rename(shape_fn.fullPathName(), f'{self._name}_{self._side}_{str(self._index).zfill(2)}Shape') for shape_fn in self._ctrl_data.shapes_fn]

    def extra_groups(self, *args):

        groups_data = {}
        self.extra_groups = []
        for arg in args:
            grp = cmds.group(self.ctrl, name=self.ctrl.replace('ctrl_', '{}_'.format(arg)))

            groups_data['{}Grp'.format(arg.lower())] = grp

            self.extra_groups.append(grp)

        return groups_data

    def match_transforms(self, obj=None, objType=None, coords=None, pos=True, rot=True, scale=False):
        """ This method matches controller translation and rotation to desired object.
        Args:
            obj (str): Object to match translates and rotates to.
        """
        obj = ou.node_with_attr(obj, objType)
        if not coords and obj:
            if cmds.objExists(obj):
                cmds.matchTransform(self.os_grp,
                                  obj,
                                  position=pos,
                                  rotation=rot,
                                  scale=scale)
            else:
                raise ValueError('This object does not exists. Please specify an object to match transforms')

        if coords and not obj:
            cmds.xform(self.os_grp, translation=coords, worldSpace=True)
        
        return
    
    def create_meta_data(self):
        super().create_meta_data()

        self.data['parameters'] = convert_list_to_str([self._side,self._name,self._shape_name])

        self.data['control'] = self._ctrl_data.dag_path
        self.data['srt_offset'] = self._srt_offset_data.dag_path
        self.data['shapes'] = self._ctrl_data.shapes
        self.data['side'] = self._side
        self.data['name'] = self._name
        self.data['shape'] = self._shape_name
        self.data['scale'] = self._scale
        self.data['index'] = self._index
        self.data['thickness'] = self._thickness
        self.data['color'] = self._color

        return self.data

    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.control = DagNodeData(data['control'])
        cls.instance.thickness = float(data['thickness'])
        cls.instance.color = data['color']

        return cls.instance
    



















'''
class Ctrl:
    """ This class creates and manipulates an animation control and its structure """

    def __init__(self,
                 shape='circle',
                 name='RENAME_ME',
                 scale=1,
                 subs=True):

        self.ctrl_name = name
        self.scale = scale
        self.subs = subs
        self.sub_a_ctrl = None
        self.sub_b_ctrl = None
        self.extraGrps = []
        self.originOffset = None
        self.originCtrl = None

        # ---  CREATE CONTROL
        self._create(shape)

    def _create(self, shape):
        """ This function creates the animation control.
        Args:
            shape (str): Desired control shape.
        """
        self.os_grp, self.ctrl, self.shapes = control_shapes.shapes(shape)

        # ---  Rename control
        self.rename(self.ctrl_name)

        # ---  Set the default shape thickness to 1
        self.thickness(1)

        # ---  Set the default color
        if self.ctrl.startswith('ctrl_l_'):
            self.color('blue')
        elif self.ctrl.startswith('ctrl_r_'):
            self.color('red')
        else:
            self.color('yellow')

        # ---  Lock visibility by default
        self.lock_visibility(True)

        # ---  Set the scale of the shape
        self.scale_ctrl(self.scale)

        # ---  Create sub controls
        if self.subs:
            self._create_sub_ctrls(0.9)

        # ---  Lock scale attributes by default
        self.lock_transforms('scale')

    def get_ctrl_os(self):
        return self.os_grp.name()

    def get_ctrl_transform(self):
        return self.ctrl.name()

    def get_ctrl_shape(self):
        return self.shapes

    def get_last_sub(self):
        return self.sub_b_ctrl[0].name()

    def _create_sub_ctrls(self, value):
        """ This method renames the control and all of its groups.
        Args:
            value (int): How many sub controls to be created.
        """
        self.sub_a_ctrl = cmds.duplicate(self.ctrl,
                                       name='{}_sub001'.format(self.ctrl))

        self.sub_b_ctrl = cmds.duplicate(self.ctrl,
                                       name='{}_sub002'.format(self.ctrl))

        cmds.parent(self.sub_a_ctrl, self.ctrl)
        cmds.parent(self.sub_b_ctrl, self.sub_a_ctrl[0])

        for sub in [self.sub_a_ctrl[0],self.sub_b_ctrl[0]]:
            for axis in 'xyz':
                sub.attr('s{}'.format(axis)).set(lock=False)
                sub.attr('s{}'.format(axis)).set(keyable=True)

        for sub in [self.sub_a_ctrl[0], self.sub_b_ctrl[0]]:
            for axis in 'xyz':
                sub.attr('s{}'.format(axis)).set(value)
                sub.attr('s{}'.format(axis)).set(keyable=False)

            cmds.makeIdentity(sub, scale=True, apply=True)
            sub.scale.set(lock=True)

        for control in [self.ctrl, self.sub_a_ctrl]:
            cmds.addAttr(control,
                       ln='Sub_Vis',
                       at='enum',
                       enumName='Hide:Show',
                       defaultValue=0,
                       keyable=True)

        self.ctrl.Sub_Vis.connect(self.sub_a_ctrl[0].getShape().visibility)
        self.sub_a_ctrl[0].Sub_Vis.connect(self.sub_b_ctrl[0].getShape().visibility)

    def rename(self, prefix):
        """ This method renames the control and all of its groups.
        Args:
            prefix (str): New desired name.
        """
        cmds.rename(self.os_grp, prefix.replace('ctrl', 'offset'))
        ctrl_name = cmds.rename(self.ctrl, prefix)

        # for i, shape in enumerate(self.shapes):
        #     print(shape)
        #     cmds.rename(shape, '{}Shape{}'.format(ctrl_name, (i+1)))

    def thickness(self, value):
        """ This method sets the curve thickness value.
        Args:
            value (int): New desired control thickness value.
        """
        for shape in self.shapes:
            cmds.setAttr(f'{shape}.lineWidth', value)

    def color(self, color):
        """ This method sets the control shape color.
        Args:
            color (str): Name of desired color. Examples are 'red', 'blue', 'yellow'
        """
        color_data = {'red': 13,
                      'blue': 6,
                      'yellow': 17}

        # ---  Check if color is valid
        if color in color_data:
            for key, value in color_data.items():
                if color == key:
                    for shape in self.shapes:
                        if shape.overrideEnabled.get() != 1:
                            shape.overrideEnabled.set(1)
                        shape.overrideColor.set(color_data[key])
        else:
            cmds.warning('Please provide a valid color name')

    def match_transforms(self, obj=None, coords=None):
        """ This method matches controller translation and rotation to desired object.
        Args:
            obj (str): Object to match translates and rotates to.
        """
        if not coords and obj:
            if cmds.objExists(obj):
                cmds.matchTransform(self.os_grp,
                                  obj,
                                  position=True,
                                  rotation=True,
                                  scale=False)
            else:
                cmds.warning('This object does not exists. Please specify an object to match transforms')

        if coords and not obj:
            cmds.xform(self.os_grp, translation=coords, worldSpace=True)

    def match_translate(self, obj):
        """ This method matches controller translation to desired object.
        Args:
            obj (str): Object to match translates to.
        """
        if cmds.objExists(obj):
            cmds.matchTransform(self.os_grp,
                              obj,
                              position=True,
                              rotation=False,
                              scale=False)
        else:
            cmds.warning('This object does not exists. Please specify an object to match translates')

    def match_rotate(self, obj):
        """ This method matches controller rotation to desired object.
        Args:
            obj (str): Object to match rotates to.
        """
        if cmds.objExists(obj):
            cmds.matchTransform(self.os_grp,
                              obj,
                              position=False,
                              rotation=True,
                              scale=False)
        else:
            cmds.warning('This object does not exists. Please specify an object to match rotates')

    def scale_ctrl(self, value):
        """ This method scales the controller to the desired value.
        Args:
            value (int): New scale value.
        """
        self.unlock_transforms('scale')

        for axis in 'xyz':
            self.ctrl.attr('s{}'.format(axis)).set(value)
        cmds.makeIdentity(self.ctrl, scale=True, apply=True)

        self.lock_transforms('scale')

    def extra_groups(self, *args):
        """ Create extra groups for the control and parents them in order of input.
        Example: "Auto" on a control named "My_Ctrl" would end up "My_Ctrl_Auto_Grp".
        Args:
            *args (str): Desired names of new groups.
        Returns (dict): Newly created groups.
        """
        groups_data = {}
        for arg in args:
            grp = cmds.group(self.ctrl, name=self.ctrl.replace('ctrl_', '{}_'.format(arg)))

            groups_data['{}Grp'.format(arg.lower())] = grp

            self.extraGrps.append(grp)

        return groups_data

    def lock_visibility(self, lock=True):
        """ This method locks & hides or unlocks & shows the visibility attribute
        of the control.
        Args:
            lock (bool): True to lock and hide, False to unlock and show.
        """
        try:
            if lock or not lock:
                self.ctrl.visibility.set(lock=lock, keyable=not lock)
        except TypeError:
            cmds.warning('Please provide either True or False')

    def lock_transforms(self, *args):
        """ This method locks given transforms.
        Accepted inputs are 'translate' or 't', 'rotate' or 'r' and 'scale' or 's'.
        Args:
            *args (str): Desired transform to lock.
        """
        axes = 'xyz'

        for arg in args:
            if arg in ('translate', 't'):
                for axis in axes:
                    self.ctrl.attr('t'+axis).set(lock=True, keyable=False)
                    # ---  Check if control has subs
                    if self.subs:
                        self.sub_a_ctrl[0].attr('t' + axis).set(lock=True, keyable=False)
                        self.sub_b_ctrl[0].attr('t' + axis).set(lock=True, keyable=False)
            if arg in ('rotate', 'r'):
                for axis in axes:
                    self.ctrl.attr('r'+axis).set(lock=True, keyable=False)
                    # ---  Check if control has subs
                    if self.subs:
                        self.sub_a_ctrl[0].attr('r' + axis).set(lock=True, keyable=False)
                        self.sub_b_ctrl[0].attr('r' + axis).set(lock=True, keyable=False)
            if arg in ('scale', 's'):
                for axis in axes:
                    self.ctrl.attr('s'+axis).set(lock=True, keyable=False)

    def unlock_transforms(self, *args):
        """ This method unlocks given transforms.
        Accepted inputs are 'translate' or 't', 'rotate' or 'r' and 'scale' or 's'.
        Args:
            *args (str): Desired transform to unlock.
        """
        axes = 'xyz'

        for arg in args:
            if arg in ('translate', 't'):
                for axis in axes:
                    self.ctrl.attr('t'+axis).set(lock=False, keyable=True)
                    # ---  Check if control has subs
                    if self.subs:
                        self.sub_a_ctrl.attr('t' + axis).set(lock=False, keyable=True)
                        self.sub_b_ctrl.attr('t' + axis).set(lock=False, keyable=True)
            if arg in ('rotate', 'r'):
                for axis in axes:
                    self.ctrl.attr('r'+axis).set(lock=False, keyable=True)
                    # ---  Check if control has subs
                    if self.subs:
                        self.sub_a_ctrl.attr('r' + axis).set(lock=False, keyable=True)
                        self.sub_b_ctrl.attr('r' + axis).set(lock=False, keyable=True)
            if arg in ('scale', 's'):
                for axis in axes:
                    self.ctrl.attr('s'+axis).set(lock=False, keyable=True)
                    # ---  Check if control has subs
                    # ---  if self.subs:
                    # ---      self.sub_a_ctrl.attr('s' + axis).set(lock=False, keyable=True)
                    # ---      self.sub_b_ctrl.attr('s' + axis).set(lock=False, keyable=True)

    def parent_to(self, obj):
        cmds.parent(self.os_grp, obj)

    def createJoint(self):
        jnt = cmds.createNode('joint', name=self.ctrl_name.replace('ctrl_', 'ctrlJnt_'), skipSelect=True)
        cmds.matchTransform(jnt, self.ctrl_name)
        jnt.visibility.set(0)

        if self.subs:
            cmds.parent(jnt, self.sub_b_ctrl)
        else:
            cmds.parent(jnt, self.ctrl_name)

    def createAtOriginCtrl(self, connectExtraGrps=True, skipGrps=[]):

        self.originOffset = cmds.createNode('transform', name='{}_Origin'.format(self.get_ctrl_os()))
        cmds.matchTransform(self.originOffset, self.get_ctrl_os())

        if self.extraGrps:
            for grp in self.extraGrps:
                extraGrp = cmds.createNode('transform', name='{}_Origin'.format(grp))
                cmds.matchTransform(extraGrp, grp)
                cmds.parent(extraGrp, '{}_Origin'.format(grp.getParent()))

                if connectExtraGrps:
                    for skipGrp in skipGrps:
                        if grp.split('_')[0] != skipGrp:
                            grp.translate.connect(extraGrp.translate)
                            grp.rotate.connect(extraGrp.rotate)
                            grp.scale.connect(extraGrp.scale)

        self.originCtrl = cmds.createNode('transform', name='{}_Origin'.format(self.get_ctrl_transform()))
        cmds.matchTransform(self.originCtrl, self.get_ctrl_transform())
        cmds.parent(self.originCtrl, '{}_Origin'.format(cmds.listRelatives(self.get_ctrl_transform(), parent=True)[0]))

        self.ctrl.translate.connect(self.originCtrl.translate)
        self.ctrl.rotate.connect(self.originCtrl.rotate)
        self.ctrl.scale.connect(self.originCtrl.scale)
'''
