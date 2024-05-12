
import maya.cmds as cmds

from dev.utils import convert_list_to_str

from rig.objects.base_object import BaseObject
from rig.objects.object_data import DagNodeData, MetaNode


class Control(BaseObject):

    SHAPES = ['circle', 'square', 'box', 'cone', 'orb', 'arrow4way', 'arrow1way', 'arrow2way', 
              'diamond', 'arrowSquare', 'diamondCross', 'triangle']
    
    COLORS = {'red': 13, 'blue': 6, 'yellow': 17}

    def __init__(self, name, side, desc, index, shape):
        super().__init__()

        self._name = name
        self._side = side
        self._desc = desc
        self._index = index
        self._shape = shape

        self._combined_name = f'{self._name}_{self._side}_{self._desc}_{str(self._index).zfill(3)}'
        
        self._ctrl = None
        self._offset = None
        self._shapes = None

        self._scale = 1.0
        self._thickness = 1.0
        self._color = 'yellow'

        self._meta_node = None

    #... Public methods ...#
    def create(self):
        """
        Creates the control.

        If the control's metadata already exists, it rebuilds the control using the existing metadata.
        Otherwise, it creates a new control based on the specified shape.

        Returns:
            The created control.
        Raises:
            ValueError: If an invalid control shape is specified.
        """
        
        if cmds.objExists(f'{self._combined_name}_ctrl_metaData'):
            self = MetaNode.rebuild(f'{self._combined_name}_ctrl_metaData')
        else:
            if self._shape in self.SHAPES:
                shape_method = getattr(ControlShapes, self._shape)
                self._ctrl = DagNodeData(shape_method(self._combined_name))
            else:
                raise ValueError(f'Please pick a control shape. Available shapes: {self.SHAPES}')
            
            self._offset = DagNodeData(cmds.createNode('transform', 
                                        name=f'{self._combined_name}_hrc'))

            cmds.parent(self._ctrl.dag_path, self._offset.dag_path)

            self._shapes = self._ctrl.shapes
            
            self.data = self._create_meta_data()
            self._create_meta_node(f'{self._combined_name}_ctrl')

            if self._side   == 'l': self._color = 'blue'
            elif self._side == 'r': self._color = 'red'
            else:                   self._color = 'yellow'

            self._set_color(self._color)

        return self

    def lock_transforms(self, node, chs='trs', axis='xyz', unlock=False):
        """
        Locks or unlocks the specified transform attributes of a given node.

        Args:
            node (str): The name of the node to lock/unlock the transform attributes for.
            chs (str, optional): The transform channels to lock/unlock. Defaults to 'trs'.
            axis (str, optional): The axes to lock/unlock. Defaults to 'xyz'.
            unlock (bool, optional): If True, unlocks the specified attributes. If False, locks them. Defaults to False.
        """
        [cmds.setAttr(f'{self._ctrl.dag_path}.{ch}{ax}', lock=not unlock) for ch in chs for ax in axis]
    
    @classmethod
    def from_data(cls, meta_node, data):
        super().from_data(meta_node, data)
        
        cls.instance.control = DagNodeData(data['control'])
        cls.instance.offset = DagNodeData(data['offset'])
        cls.instance.thickness = float(data['thickness'])
        cls.instance.color = data['color']

        return cls.instance
    
    #... Private methods ...#
    def _set_color(self, value):
        """
        Sets the color of the control.

        Args:
            value (str): The color name to set.

        Returns:
            int: The color index that was set.

        Raises:
            ValueError: If an invalid color name is provided.
        """
        if value in self.COLORS:
            color = self.COLORS[value]

            if hasattr(self, '_ctrl'):
                shapes = [shape.fullPathName() for shape in self._ctrl.shapes]
            else: 
                shapes =  [self.data[key].fullPathName() for key in self.data.keys() if key.startswith('shapes_') and key[-1].isdigit()]

            for shape in shapes:
                if not cmds.getAttr(f'{shape}.overrideEnabled'):
                    cmds.setAttr(f'{shape}.overrideEnabled', 1)
                cmds.setAttr(f'{shape}.overrideColor', color)
            
            if hasattr(self, 'meta_node'):
                cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.color', lock=False)
                cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.color', value, type='string', lock=True)
        else:
            raise ValueError('Please provide a valid color name')
        
        return color

    def _set_thickness(self, value):  
        """
        Sets the thickness of the control's shapes.

        Args:
            value (float): The desired thickness value.

        Returns:
            None
        """
        if hasattr(self, '_ctrl'):
            shapes = [shape.fullPathName() for shape in self._ctrl.shapes]
        else: 
            shapes =  [self.data[key].fullPathName() for key in self.data.keys() if key.startswith('shapes_') and key[-1].isdigit()]
        
        [cmds.setAttr(f'{shape}.lineWidth', value) for shape in shapes]

        if hasattr(self, 'meta_node'):
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.thickness', lock=False)
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.thickness', value, lock=True)

    def _set_scale(self, value):
        """
        Sets the scale of the control.

        Args:
            value (float): The scale value to set.

        Returns:
            None
        """
        self.lock_transforms(self._ctrl.dag_path, 's', unlock=True)

        for axis in 'xyz':
            cmds.setAttr(f'{self._ctrl.dag_path}.s{axis}', value)
        cmds.makeIdentity(self._ctrl.dag_path, scale=True, apply=True)

        self.lock_transforms(self._ctrl.dag_path, 's')

        if hasattr(self, 'meta_node'):
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.scale', lock=False)
            cmds.setAttr(f'{self.meta_node.dependnode_fn.absoluteName()}.scale', value, lock=True)

    def _create_meta_data(self):
        super()._create_meta_data()

        self.data['parameters'] = convert_list_to_str([self._name,
                                                                    self._side,
                                                                    self._desc,
                                                                    self._index,
                                                                    self._shape])

        self.data['control'] = self._ctrl.dag_path
        self.data['offset'] = self._offset.dag_path
        self.data['shapes'] = self._ctrl.shapes
        self.data['side'] = self._side
        self.data['name'] = self._name
        self.data['shape'] = self._shape
        self.data['scale'] = self._scale
        self.data['index'] = self._index
        self.data['thickness'] = self._thickness
        self.data['color'] = self._color

        return self.data

    #... Properties ...#
    @property
    def meta_node(self):
        return self._meta_node
    
    @meta_node.setter
    def meta_node(self, value):
        self._meta_node = value

    @property
    def control(self):
        return self._ctrl
    
    @control.setter
    def control(self, value):
        self._ctrl = value

    @property
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):            
        self._color = self._set_color(value)

    @property
    def thickness(self):
        return self._thickness
    
    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        self._set_thickness(self._thickness)
    
    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self._scale = value
        self._set_scale(self._scale)
    

class ControlShapes:

    @staticmethod
    def create_shape(name, positions, degree=1, close=False):
        """
        Creates a control shape based on the given positions.

        Args:
            positions (list): A list of positions to create the control shape.

        Returns:
            str: The name of the transform node representing the control shape.
        """
        temp_transforms = []

        for pos in positions:
            crv = cmds.curve(d=degree, p=pos)
            if close:
                cmds.closeCurve(crv, ch=True, ps=False, rpo=True)
            temp_transforms.append(crv)

        crv_transform = cmds.createNode('transform', name=f'{name}_ctrl')
        for temp_transform in temp_transforms:
            shape = cmds.listRelatives(temp_transform, shapes=True)
            shape = cmds.rename(shape, f'{name}_ctrlShape_001')
            cmds.parent(shape, crv_transform, r=True, shape=True)

        cmds.delete(temp_transforms)

        return crv_transform

    @classmethod
    def circle(cls, name):
        """ circle shape """

        pos = []
        pos.append( (0.39180581244561224, 2.3991186704942366e-17, -0.3918058124456123) )
        pos.append( (3.392866161555456e-17, 3.392866161555456e-17, -0.5540970937771938) )
        pos.append( (-0.39180581244561224, 2.399118670494236e-17, -0.3918058124456122) )
        pos.append( (-0.5540970937771941, 1.7588678095030136e-33, -2.872449118762415e-17) )
        pos.append( (-0.39180581244561224, -2.3991186704942363e-17, 0.39180581244561224) )
        pos.append( (-5.5504284848016124e-17, -3.3928661615554586e-17, 0.5540970937771942) )
        pos.append( (0.39180581244561224, -2.399118670494236e-17, 0.3918058124456122) )
        pos.append( (0.5540970937771941, -4.6268396050550495e-33, 7.556202503899795e-17) )

        return cls.create_shape(name,[pos], 2, True)

    @classmethod
    def square(cls, name):
        """
        square shape
        """

        pos = []
        pos.append((-1.000000, 0.000000, 1.000000))
        pos.append((-1.000000, 0.000000, -1.000000))
        pos.append((1.000000, 0.000000, -1.000000))
        pos.append((1.000000, 0.000000, 1.000000))

        return cls.create_shape(name,[pos])

    @classmethod
    def arrowSquare(cls, name):
        """ arrow-square shape """

        pos = []
        pos.append( ( 0.510003, 0.000000, -0.382900 ) )
        pos.append( ( 0.510003, 0.000000, 0.382900 ) )
        pos.append( ( 0.000000, 0.000000, 0.765800 ) )
        pos.append( ( -0.510003, 0.000000, 0.382900 ) )
        pos.append( ( -0.510003, 0.000000, -0.382900 ) )

        return cls.create_shape(name, [pos], close=True)

    @classmethod
    def box(cls, name):
        """ box shape """

        pos = []
        pos.append( ( 0.500000, 0.499745, 0.500000 ) )
        pos.append( ( -0.500000, 0.499745, 0.500000 ) )
        pos.append( ( -0.500000, -0.500255, 0.500000 ) )
        pos.append( ( 0.500000, -0.500255, 0.500000 ) )
        pos.append( ( 0.500000, 0.499745, 0.500000 ) )
        pos.append( ( 0.500000, 0.499745, -0.500000 ) )
        pos.append( ( 0.500000, -0.500255, -0.500000 ) )
        pos.append( ( 0.500000, -0.500255, 0.500000 ) )
        pos.append( ( 0.500000, 0.499745, 0.500000 ) )
        pos.append( ( 0.500000, 0.499745, -0.500000 ) )
        pos.append( ( -0.500000, 0.499745, -0.500000 ) )
        pos.append( ( -0.500000, -0.500255, -0.500000 ) )
        pos.append( ( 0.500000, -0.500255, -0.500000 ) )
        pos.append( ( -0.500000, -0.500255, -0.500000 ) )
        pos.append( ( -0.500000, -0.500255, 0.500000 ) )
        pos.append( ( -0.500000, 0.499745, 0.500000 ) )
        pos.append( ( -0.500000, 0.499745, -0.500000 ) )

        return cls.create_shape(name,[pos])

    @classmethod
    def triangle(cls, name):
        """ triangle shape """

        pos = []
        pos.append( ( -0.500000, 0.000000, -0.500000 ) )
        pos.append( ( 0.000000, 0.000000, 0.500000 ) )
        pos.append( ( 0.500000, 0.000000, -0.500000 ) )

        return cls.create_shape(name, [pos], close=True)

    @classmethod
    def cone(cls, name):
        """ cone shape """

        pos = []
        pos.append( ( -0.250000, 0.000000, 0.433013 ) )
        pos.append( ( 0.000000, 1.000000, 0.000000 ) )
        pos.append( ( 0.250000, 0.000000, 0.433013 ) )
        pos.append( ( -0.250000, 0.000000, 0.433013 ) )
        pos.append( ( -0.500000, 0.000000, -0.000000 ) )
        pos.append( ( 0.000000, 1.000000, 0.000000 ) )
        pos.append( ( -0.500000, 0.000000, -0.000000 ) )
        pos.append( ( -0.250000, 0.000000, -0.433013 ) )
        pos.append( ( 0.000000, 1.000000, 0.000000 ) )
        pos.append( ( 0.250000, 0.000000, -0.433013 ) )
        pos.append( ( -0.250000, 0.000000, -0.433013 ) )
        pos.append( ( 0.250000, 0.000000, -0.433013 ) )
        pos.append( ( 0.000000, 1.000000, 0.000000 ) )
        pos.append( ( 0.500000, 0.000000, 0.000000 ) )
        pos.append( ( 0.250000, 0.000000, -0.433013 ) )
        pos.append( ( 0.500000, 0.000000, 0.000000 ) )
        pos.append( ( 0.250000, 0.000000, 0.433013 ) )

        return cls.create_shape(name, [pos])

    @classmethod
    def orb(cls, name):
        """ orb shape """

        pos = []
        ####################################################
        pos.append( ( 0.391806, -0.391806, 0.000000 ) )
        pos.append( ( 0.000000, -0.554097, 0.000000 ) )
        pos.append( ( -0.391806, -0.391806, 0.000000 ) )
        pos.append( ( -0.554097, -0.000000, 0.000000 ) )
        pos.append( ( -0.391806, 0.391806, 0.000000 ) )
        pos.append( ( -0.000000, 0.554097, 0.000000 ) )
        pos.append( ( 0.391806, 0.391806, 0.000000 ) )
        pos.append( ( 0.554097, -0.000000, 0.000000 ) )
        ####################################################
        pos2 = []
        pos2.append( ( 0.391806, 0.000000, -0.391806 ) )
        pos2.append( ( 0.000000, 0.000000, -0.554097 ) )
        pos2.append( ( -0.391806, 0.000000, -0.391806 ) )
        pos2.append( ( -0.554097, 0.000000, -0.000000 ) )
        pos2.append( ( -0.391806, -0.000000, 0.391806 ) )
        pos2.append( ( -0.000000, -0.000000, 0.554097 ) )
        pos2.append( ( 0.391806, -0.000000, 0.391806 ) )
        pos2.append( ( 0.554097, -0.000000, 0.000000 ) )
        ####################################################
        pos3 = []
        pos3.append( ( 0.000000, -0.391806, -0.391806 ) )
        pos3.append( ( 0.000000, -0.000000, -0.554097 ) )
        pos3.append( ( 0.000000, 0.391806, -0.391806 ) )
        pos3.append( ( -0.000000, 0.554097, -0.000000 ) )
        pos3.append( ( -0.000000, 0.391806, 0.391806 ) )
        pos3.append( ( -0.000000, 0.000000, 0.554097 ) )
        pos3.append( ( -0.000000, -0.391806, 0.391806 ) )
        pos3.append( ( 0.000000, -0.554097, 0.000000 ) )

        return cls.create_shape(name, [pos, pos2, pos3], 3, True)

    @classmethod
    def diamond(cls, name):
        """ diamond shape """

        pos = []
        pos.append((-1.000000, 0.000000, 0.000000))
        pos.append((0.000000, 1.000000, 0.000000))
        pos.append((1.000000, 0.000000, 0.000000))
        pos.append((0.000000, -1.000000, 0.000000))
        pos.append((-1.000000, 0.000000, 0.000000))
        pos.append((0.000000, 1.000000, 0.000000))
        pos.append((0.000000, 0.000000, 1.000000))
        pos.append((0.000000, -1.000000, 0.000000))
        pos.append((0.000000, 0.000000, -1.000000))
        pos.append((0.000000, 1.000000, 0.000000))
        pos.append((-1.000000, 0.000000, 0.000000))
        pos.append((0.000000, 0.000000, 1.000000))
        pos.append((1.000000, 0.000000, 0.000000))
        pos.append((0.000000, 0.000000, -1.000000))
        pos.append((-1.000000, 0.000000, 0.000000))

        return cls.create_shape(name, [pos])

    @classmethod
    def diamondCross(cls, name):
        """ diamondCross shape """

        pos = []

        pos.append( ( 0.000000, 0.000000, 0.000000 ) )
        pos.append( ( 0.000000, 0.000000, -0.496386 ) )
        pos.append( ( -0.248193, 0.000000, -0.744578 ) )
        pos.append( ( 0.000000, 0.000000, -0.992771 ) )
        pos.append( ( 0.248193, 0.000000, -0.744578 ) )
        pos.append( ( 0.000000, 0.000000, -0.496386 ) )
        pos.append( ( 0.000000, 0.000000, 0.000000 ) )
        pos.append( ( 0.496386, 0.000000, 0.000000 ) )
        pos.append( ( 0.744578, 0.000000, -0.248193 ) )
        pos.append( ( 0.992771, 0.000000, 0.000000 ) )
        pos.append( ( 0.744578, 0.000000, 0.248193 ) )
        pos.append( ( 0.496386, 0.000000, 0.000000 ) )
        pos.append( ( 0.000000, 0.000000, 0.000000 ) )
        pos.append( ( 0.000000, 0.000000, 0.496386 ) )
        pos.append( ( 0.248193, 0.000000, 0.744578 ) )
        pos.append( ( 0.000000, 0.000000, 0.992771 ) )
        pos.append( ( -0.248193, 0.000000, 0.744578 ) )
        pos.append( ( 0.000000, 0.000000, 0.496386 ) )
        pos.append( ( 0.000000, 0.000000, 0.000000 ) )
        pos.append( ( -0.496386, 0.000000, 0.000000 ) )
        pos.append( ( -0.744578, 0.000000, 0.248193 ) )
        pos.append( ( -0.992771, 0.000000, 0.000000 ) )
        pos.append( ( -0.744578, 0.000000, -0.248193 ) )
        pos.append( ( -0.496386, 0.000000, 0.000000 ) )
        pos.append( ( 0.000000, 0.000000, 0.000000 ) )

        return cls.create_shape(name, [pos])

    @classmethod
    def arrow1way(cls, name):
        
        pos = []
        pos.append( (0.3535533547401428, 0.0, -0.3535533547401428) )
        pos.append( (0.0, 0.0, -0.4999999403953552) )
        pos.append( (-0.3535533547401428, 0.0, -0.3535533547401428) )
        pos.append( (-0.5, 0.0, 0.0) )
        pos.append( (-0.3535533845424652, 0.0, 0.3535533845424652) )
        pos.append( (-0.1767766922712326, 0.0, 0.4267766773700714) )
        pos.append( (-0.1767766922712326, 0.0, 0.4619667547499593) )
        pos.append( (-0.31628113985061646, 0.0, 0.4619667547499593) )
        pos.append( (0.0, 0.0, 0.7457171695982869) )
        pos.append( (0.31628113985061646, 0.0, 0.4619667547499593) )
        pos.append( (0.1767766922712326, 0.0, 0.4619667547499593) )
        pos.append( (0.1767766922712326, 0.0, 0.4267766773700714) )
        pos.append( (0.3535533845424652, 0.0, 0.3535533845424652) )
        pos.append( (0.5, 0.0, 0.0) )

        pos2 = []
        pos2.append( (-0.1767766922712326, 0.0, 0.4267766773700714) )
        pos2.append( (-0.1767766922712326, 0.06717795332053328, 0.4619667547499593) )
        pos2.append( (-0.31628113985061646, 0.06717795332053328, 0.4619667547499593) )
        pos2.append( (0.0, 0.06717795332053328, 0.7457171695982869) )
        pos2.append( (0.31541842222213745, 0.06717795332053328, 0.46194371581077576) )
        pos2.append( (0.1769469833419921, 0.06717795332053328, 0.4619667547499593) )
        pos2.append( (0.1767766922712326, 0.0, 0.4267766773700714) )

        return cls.create_shape(name, [pos, pos2], close=True)

    @classmethod
    def arrow4way(cls, name):
        """ COG shape """

        pos = []

        pos.append( ( -0.134942, 0.000000, -0.269883 ) )
        pos.append( ( -0.134942, 0.000000, -0.404825 ) )
        pos.append( ( -0.269883, 0.000000, -0.404825 ) )
        pos.append( ( 0.000000, 0.000000, -0.674708 ) )
        pos.append( ( 0.269883, 0.000000, -0.404825 ) )
        pos.append( ( 0.134942, 0.000000, -0.404825 ) )
        pos.append( ( 0.134942, 0.000000, -0.269883 ) )
        pos.append( ( 0.269883, 0.000000, -0.134942 ) )
        pos.append( ( 0.404825, 0.000000, -0.134942 ) )
        pos.append( ( 0.404825, 0.000000, -0.269883 ) )
        pos.append( ( 0.674708, 0.000000, 0.000000 ) )
        pos.append( ( 0.404825, 0.000000, 0.269883 ) )
        pos.append( ( 0.404825, 0.000000, 0.134942 ) )
        pos.append( ( 0.269883, 0.000000, 0.134942 ) )
        pos.append( ( 0.134942, 0.000000, 0.269883 ) )
        pos.append( ( 0.134942, 0.000000, 0.404825 ) )
        pos.append( ( 0.269883, 0.000000, 0.404825 ) )
        pos.append( ( 0.000000, 0.000000, 0.674708 ) )
        pos.append( ( -0.269883, 0.000000, 0.404825 ) )
        pos.append( ( -0.134942, 0.000000, 0.404825 ) )
        pos.append( ( -0.134942, 0.000000, 0.269883 ) )
        pos.append( ( -0.269883, 0.000000, 0.134942 ) )
        pos.append( ( -0.404825, 0.000000, 0.134942 ) )
        pos.append( ( -0.404825, 0.000000, 0.269883 ) )
        pos.append( ( -0.674708, 0.000000, 0.000000 ) )
        pos.append( ( -0.404825, 0.000000, -0.269883 ) )
        pos.append( ( -0.404825, 0.000000, -0.134942 ) )
        pos.append( ( -0.269883, 0.000000, -0.134942 ) )

        return cls.create_shape(name, [pos], close=True)

    @classmethod
    def arrow2way(cls, name):
        """ COG shape """

        pos = []

        pos.append( (-0.3535533845424652, 0.0, 0.3535533845424652) )
        pos.append( (-0.1767766922712326, 0.0, 0.42653024196624756) )
        pos.append( (-0.1767767071723938, 0.0, 0.46196675300598145) )
        pos.append( (-0.31628113985061646, 0.0, 0.46196675300598145) )
        pos.append( (0.0, 0.0, 0.7439941763877869) )
        pos.append( (0.31628113985061646, 0.0, 0.46196675300598145) )
        pos.append( (0.1767767071723938, 0.0, 0.46196675300598145) )
        pos.append( (0.1767766922712326, 0.0, 0.42653024196624756) )
        pos.append( (0.3535533845424652, 0.0, 0.3535533845424652) )
        pos.append( (0.5, 0.0, 0.0) )
        pos.append( (0.3535533845424652, 0.0, -0.3535533845424652) )
        pos.append( (0.1767766922712326, 0.0, -0.42653024196624756) )
        pos.append( (0.1767767071723938, 0.0, -0.46196675300598145) )
        pos.append( (0.31628113985061646, 0.0, -0.46196675300598145) )
        pos.append( (0.0, 0.0, -0.7439941763877869) )
        pos.append( (-0.31628113985061646, 0.0, -0.46196675300598145) )
        pos.append( (-0.1767767071723938, 0.0, -0.46196675300598145) )
        pos.append( (-0.1767766922712326, 0.0, -0.42653024196624756) )
        pos.append( (-0.3535533845424652, 0.0, -0.3535533845424652) )
        pos.append( (-0.5, 0.0, 0.0) )

        pos2 = []
        pos2.append( (-0.1767766922712326, 0.0, 0.4267766773700714) )
        pos2.append( (-0.1767766922712326, 0.06717795332053328, 0.4619667547499593) )
        pos2.append( (-0.31628113985061646, 0.06717795332053328, 0.4619667547499593) )
        pos2.append( (0.0, 0.06717795332053328, 0.7457171695982869) )
        pos2.append( (0.31541842222213745, 0.06717795332053328, 0.46194371581077576) )
        pos2.append( (0.1769469833419921, 0.06717795332053328, 0.4619667547499593) )
        pos2.append( (0.1767766922712326, 0.0, 0.4267766773700714) )

        pos3 = []
        pos3.append( (-0.1767766922712326, 0.0, -0.4267766773700714) )
        pos3.append( (-0.1767766922712326, 0.06717795332053328, -0.4619667547499593) )
        pos3.append( (-0.31628113985061646, 0.06717795332053328, -0.4619667547499593) )
        pos3.append( (0.0, 0.06717795332053328, -0.7457171695982869) )
        pos3.append( (0.31541842222213745, 0.06717795332053328, -0.46194371581077576) )
        pos3.append( (0.1769469833419921, 0.06717795332053328, -0.4619667547499593) )
        pos3.append( (0.1767766922712326, 0.0, -0.4267766773700714) )

        return cls.create_shape(name, [pos,pos2,pos3], close=True)

