
import maya.cmds as cmds

class ControlShapes:

    SHAPES = ['circle', 'square', 'box', 'cone', 'orb', 'COG', 'diamond', 
                  'arrowSquare', 'diamondCross', 'triangle']

    def __init__(self, shape):

        self._shape = shape
        self._name = None

    def create(self):
        
        if self._shape in self.SHAPES:
            shape_method = getattr(__class__, self._shape)
            self._name = shape_method(self)
        else:
            raise ValueError(f'Please pick a control shape. Available shapes: {self.SHAPES}')
        
        return self

    @property
    def name(self):
        return self._name

    def create_shape(self, positions):

        temp_transforms = []

        for pos in positions:
            crv = cmds.curve(d=1, p=pos)

            temp_transforms.append(crv)

        crv_transform = cmds.createNode('transform', name='nurbsCircle1')
        for temp_transform in temp_transforms:
            shape = cmds.listRelatives(temp_transform, shapes=True)
            cmds.parent(shape, crv_transform, r=True, shape=True)

        cmds.delete(temp_transforms)

        return crv_transform

    def circle(self, curveScale=1.0):
        """ circle shape """

        crv = cmds.circle(normal=[0,11,0], ch=False, radius=curveScale*0.5)[0]

        return crv


    def square(self, curveScale=1.0):
        """
        square shape
        """

        pos = []
        pos.append((-1.000000, 0.000000, 1.000000))
        pos.append((-1.000000, 0.000000, -1.000000))
        pos.append((1.000000, 0.000000, -1.000000))
        pos.append((1.000000, 0.000000, 1.000000))
        pos.append((-1.000000, 0.000000, 1.000000))

        return self.create_shape([pos])

    def arrowSquare(self):
        """ arrow-square shape """

        pos = []
        pos.append( ( 0.510003, 0.000000, -0.382900 ) )
        pos.append( ( 0.510003, 0.000000, 0.382900 ) )
        pos.append( ( 0.000000, 0.000000, 0.765800 ) )
        pos.append( ( -0.510003, 0.000000, 0.382900 ) )
        pos.append( ( -0.510003, 0.000000, -0.382900 ) )
        pos.append( ( 0.510003, 0.000000, -0.382900 ) )

        return self.create_shape([pos])

    def arrowSquareY(self):
        """ arrow-square shape """

        pos = []
        pos.append( ( 0.510003, 0.382900, 0.000000 ) )
        pos.append( ( 0.510003, -0.382900, -0.000000 ) )
        pos.append( ( 0.000000, -0.765800, -0.000000 ) )
        pos.append( ( -0.510003, -0.382900, -0.000000 ) )
        pos.append( ( -0.510003, 0.382900, 0.000000 ) )
        pos.append( ( 0.510003, 0.382900, 0.000000 ) )

        return self.create_shape([pos])

    def box(self):
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

        return self.create_shape([pos])

    def square(self):
        """ square shape """

        pos = []
        pos.append( ( -1.000000, 0.000000, 1.000000 ) )
        pos.append( ( -1.000000, 0.000000, -1.000000 ) )
        pos.append( ( 1.000000, 0.000000, -1.000000 ) )
        pos.append( ( 1.000000, 0.000000, 1.000000 ) )
        pos.append( ( -1.000000, 0.000000, 1.000000 ) )

        return self.create_shape([pos])

    def triangle(self):
        """ triangle shape """

        pos = []
        pos.append( ( -0.500000, 0.000000, -0.500000 ) )
        pos.append( ( 0.000000, 0.000000, 0.500000 ) )
        pos.append( ( 0.500000, 0.000000, -0.500000 ) )
        pos.append( ( -0.500000, 0.000000, -0.500000 ) )

        return self.create_shape([pos])

    def cone(self):
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

        # crv = cmds.curve(d=1, p=pos)

        # return crv

        return self.create_shape([pos])

    def orb(self):
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
        pos.append( ( 0.391806, -0.391806, 0.000000 ) )
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
        pos2.append( ( 0.391806, 0.000000, -0.391806 ) )
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
        pos3.append( ( 0.000000, -0.391806, -0.391806 ) )

        return self.create_shape([pos, pos2, pos3])

    def diamond(self):
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

        return self.create_shape([pos])

    def diamondCross(self):
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

        return self.create_shape([pos])

    def COG(self):
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
        pos.append( ( -0.134942, 0.000000, -0.269883 ) )

        return self.create_shape([pos])

    def printCvPositions(self, curve):
        """ print curve CVs positions for control function """
        shapes = cmds.listRelatives(curve, shapes=True)

        for i in shapes:
            cvs = cmds.ls(i + '.cv[*]', fl=True)

            pos_array = []

            print('#' * 20)

            for cv in cvs:
                pos = cmds.xform(cv, q=True, t=True, ws=True)
                pos_array.append(pos)
                print(f'pos.append( {tuple(pos)} )')

        return pos_array

''' 
def shapes(shape):

    osGrp = pm.group(empty=True)
    ctrl = None

    if shape == 'circle':
        ctrl = circle()
    elif shape == 'square':
        ctrl = square()
    elif shape == 'box':
        ctrl = box()
    elif shape == 'cone':
        ctrl = cone()
    elif shape == 'orb':
        ctrl = orb()
    elif shape == 'COG':
        ctrl = COG()
    elif shape == 'diamond':
        ctrl = diamond()
    elif shape == 'arrowSquare':
        ctrl = arrowSquare()
    elif shape == 'diamondCross':
        ctrl = diamondCross()
    else:
        pm.warning('Please pick a control shape')
    shape = ctrl.getShapes()

    pm.parent(ctrl, osGrp)

    return osGrp, ctrl, shape

def circle(curveScale=1.0):
    """ circle shape """

    crv = pm.circle(normal=[1,0,0], ch=False, radius=curveScale*0.5)[0]

    return crv


def square(curveScale=1.0):
    """
    square shape
    """

    pos = []
    pos.append((-1.000000, 0.000000, 1.000000))
    pos.append((-1.000000, 0.000000, -1.000000))
    pos.append((1.000000, 0.000000, -1.000000))
    pos.append((1.000000, 0.000000, 1.000000))
    pos.append((-1.000000, 0.000000, 1.000000))

    crv = pm.curve(d=1, p=pos)

    return crv

def arrowSquare():
    """ arrow-square shape """

    pos = []
    pos.append( ( 0.510003, 0.000000, -0.382900 ) )
    pos.append( ( 0.510003, 0.000000, 0.382900 ) )
    pos.append( ( 0.000000, 0.000000, 0.765800 ) )
    pos.append( ( -0.510003, 0.000000, 0.382900 ) )
    pos.append( ( -0.510003, 0.000000, -0.382900 ) )
    pos.append( ( 0.510003, 0.000000, -0.382900 ) )

    crv = pm.curve(d=1, p=pos)

    return crv

def arrowSquareY():
    """ arrow-square shape """

    pos = []
    pos.append( ( 0.510003, 0.382900, 0.000000 ) )
    pos.append( ( 0.510003, -0.382900, -0.000000 ) )
    pos.append( ( 0.000000, -0.765800, -0.000000 ) )
    pos.append( ( -0.510003, -0.382900, -0.000000 ) )
    pos.append( ( -0.510003, 0.382900, 0.000000 ) )
    pos.append( ( 0.510003, 0.382900, 0.000000 ) )

    crv = pm.curve(d=1, p=pos)

    return crv

def box():
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

    crv = pm.curve(d=1, p=pos)

    return crv

def square():
    """ square shape """

    pos = []
    pos.append( ( -1.000000, 0.000000, 1.000000 ) )
    pos.append( ( -1.000000, 0.000000, -1.000000 ) )
    pos.append( ( 1.000000, 0.000000, -1.000000 ) )
    pos.append( ( 1.000000, 0.000000, 1.000000 ) )
    pos.append( ( -1.000000, 0.000000, 1.000000 ) )

    crv = pm.curve(d=1, p=pos)

    return crv

def triangle():
    """ triangle shape """

    pos = []
    pos.append( ( -0.500000, 0.000000, -0.500000 ) )
    pos.append( ( 0.000000, 0.000000, 0.500000 ) )
    pos.append( ( 0.500000, 0.000000, -0.500000 ) )
    pos.append( ( -0.500000, 0.000000, -0.500000 ) )

    crv = pm.curve(d=1, p=pos)

    return crv

def cone():
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

    crv = pm.curve(d=1, p=pos)

    return crv

def orb():
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
    pos.append( ( 0.391806, -0.391806, 0.000000 ) )
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
    pos2.append( ( 0.391806, 0.000000, -0.391806 ) )
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
    pos3.append( ( 0.000000, -0.391806, -0.391806 ) )

    a = []

    for p in [pos, pos2, pos3]:
        crv = pm.curve(d=1, p=p)

        a.append(crv)

    crv_transform = pm.group(name='nurbsCircle1', empty=True)
    for i in a:
        b = pm.listRelatives(i, shapes=True)
        pm.parent(b, crv_transform, r=True, shape=True)

    pm.delete(a)

    return crv_transform


def diamond():
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

    crv = pm.curve(d=1, p=pos)

    return crv

def diamondCross():
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

    crv = pm.curve(d=1, p=pos)

    return crv

def COG():
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
    pos.append( ( -0.134942, 0.000000, -0.269883 ) )

    crv = pm.curve(d=1, p=pos)

    return crv


def printCvPositions(curve):
    """ print curve CVs positions for control function """
    shapes = pm.listRelatives(curve, shapes=True)

    for i in shapes:
        cvs = pm.ls(i + '.cv[*]', fl=True)

        pos_array = []

        print('#' * 20)

        for cv in cvs:
            pos = pm.xform(cv, q=True, t=True, ws=True)
            pos_array.append(pos)
            print(f'pos.append( {tuple(pos)} )')

    return pos_array
'''