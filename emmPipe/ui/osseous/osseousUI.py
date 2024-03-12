import inspect
import os
import sys
import importlib
import math

from PySide2.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsTextItem, QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget, QGraphicsProxyWidget
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QApplication
from PySide2.QtGui import QColor, QFocusEvent, QKeyEvent, QMouseEvent, QPen, QPainter, QPainterPath, QWheelEvent, Qt, QFont, QBrush, QPolygonF
from PySide2.QtCore import QLine, QEvent, QRectF, Qt, QFile, QPointF

from emmPipe.ui.utils import DockableUI

DEBUG = True

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

LEFT_TOP     = 1
LEFT_BOTTOM  = 2
RIGHT_TOP    = 3
RIGHT_BOTTOM = 4

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 10

EDGE_CP_ROUNDNESS = 100

def printDebug(DEBUG, message):
    """
    Print debug information if DEBUG is True.

    Args:
        DEBUG (bool): Flag indicating whether to print debug information.
        message (str): The debug message to be printed.
    """
    classInfo = inspect.currentframe().f_back.f_locals.get('self', None)
    if DEBUG: print(classInfo.__class__.__name__, '::', inspect.stack()[1].function, ' ~ ', message)

def debugModifiers(event):
    """
    Returns a string indicating which modifiers are active in the given event.

    Args:
        event: The event object.

    Returns:
        A string indicating the active modifiers. Possible values are 'SHIFT', 'CTRL', 'ALT', or a combination of them.

    """
    out = "MODS: "
    if event.modifiers() & Qt.ShiftModifier: out += 'SHIFT '
    if event.modifiers() & Qt.ControlModifier: out += 'CTRL '
    if event.modifiers() & Qt.AltModifier: out += 'ALT '
    return out

class OsseousUI(DockableUI):
    
    WINDOW_TITLE = 'Osseous'

    def __init__(self):
        super().__init__()
        
        filepath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        stylesheetFilename = 'qss/nodeStyle.qss'
        #self.loadStylesheet(os.path.join(filepath, stylesheetFilename))

        self.setWindowTitle('Osseous')

        self.setGeometry(200, 200, 800, 800)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.scene = NodeEditorScene()

        self.addNodes()

        self.view = NodeEditorQGraphView(self.scene.graphicsScene, self)
        self.layout.addWidget(self.view)

        self.view.setAntiAliasing()
        self.view.updateViewport()
        self.view.removeScrollBars()

    def addNodes(self):

        node1 = NodeEditorNode(self.scene, 
                               'Node1',
                              inputs=[1,2,3], 
                              outputs=[4])
        
        node2 = NodeEditorNode(self.scene, 
                               'Node2',
                              inputs=[1,2,3], 
                              outputs=[4])
        
        node3 = NodeEditorNode(self.scene, 
                               'Node3',
                              inputs=[1,2,3], 
                              outputs=[4])
        
        node1.setPosition(-350, -200)
        node3.setPosition(350, -200)

        print(' Node1: ', node1)
        print(' Node2: ', node2)

        print(' Node1 outputs: ', node1.outputs[0])
        print(' Node2 inputs: ', node2.inputs[0])


        edge1 = NodeEditorEdge(self.scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_BEZIER)
        edge2 = NodeEditorEdge(self.scene, node2.outputs[0], node3.inputs[1], EDGE_TYPE_BEZIER)

        print(' Edge1: ', edge1)
        print(' Edge2: ', edge2)
    
    def loadStylesheet(self, filename):

        with open(filename, 'r') as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)
        

class NodeEditorQGraphView(QGraphicsView):

    def __init__(self, graphicsScene, parent=None):
        super(NodeEditorQGraphView, self).__init__(None)   

        self.graphicsScene = graphicsScene     

        self.setScene(self.graphicsScene)

        self.mode = MODE_NOOP
        self.ediitingFlag = False

        self.zoomInFactor = 1.25
        self.zoomClamp = False
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        self.cutLine = NodeEditorGraphicsCutline()
        self.graphicsScene.addItem(self.cutLine)

        self.setTransformationAnchor(self.AnchorUnderMouse)

        self.setDragMode(self.RubberBandDrag)

    def setAntiAliasing(self):

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.HighQualityAntialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
    
    def updateViewport(self):

        self.setViewportUpdateMode(self.FullViewportUpdate)
    
    def removeScrollBars(self):

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)
    
    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(self.ScrollHandDrag)

        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)
    
    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), 
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(self.NoDrag)

    def leftMouseButtonPress(self, event):

        item = self.getItemAtClick(event)
        
        self.lastLMBClickScenePos = self.mapToScene(event.pos())
        
        printDebug(DEBUG, f'LMB click on {item} {debugModifiers(event)}')

        if hasattr(item, 'node') or isinstance(item, NodeEditorGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(), Qt.LeftButton,
                                        event.buttons() | Qt.LeftButton, event.modifiers() | Qt.ControlModifier) 
                super().mousePressEvent(fakeEvent)
                return

        if isinstance(item, NodeEditorGraphicsSocket):
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG

                self.edgeDragStart(item)
                
                return
        
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if not item:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):

        item = self.getItemAtClick(event)

        if hasattr(item, 'node') or isinstance(item, NodeEditorGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton,
                                        Qt.NoButton, event.modifiers() | Qt.ControlModifier) 
                super().mouseReleaseEvent(fakeEvent)
                
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return

        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutLine.linePoints = []
            self.cutLine.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            
            return

        super().mouseReleaseEvent(event)
    
    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)

        if DEBUG: 
            if isinstance(item, NodeEditorGraphicsEdge): print('RMB DEBUG:', item.edge, 'connecting sockets:',
                                                               item.edge.startSocket, '<->', item.edge.endSocket)
            if isinstance(item, NodeEditorGraphicsSocket): print('RMB DEBUG:', item.socket, 'has edge:', item.socket.edge)

            if not item:
                print('SCENE:')
                print(' Nodes:')
                for node in self.graphicsScene.scene.nodes: print('     ', node)
                print(' Edges:')
                for edge in self.graphicsScene.scene.edges: print('     ', edge)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.graphicsEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.graphicsEdge.update()
        
        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutLine.linePoints.append(pos)
            self.cutLine.update()
        
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete:
            if not self.ediitingFlag:
                self.deleteSelected()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        
        zoomOutFactor = 1 / self.zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor 
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:
            self.zoom, clamped = self.zoomRange[1], True
        
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)
    
    def getItemAtClick(self, event):

        pos = event.pos()
        obj = self.itemAt(pos)

        return obj
    
    def edgeDragStart(self, item):
        printDebug(DEBUG, 'start dragging edge')
        printDebug(DEBUG, f'assign Start Socket to: {item.socket}')
        self.previousEdge = item.socket.edge
        self.lastStartSocket = item.socket
        self.dragEdge = NodeEditorEdge(self.graphicsScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        printDebug(DEBUG, f'dragEdge: {self.dragEdge}')
    
    def edgeDragEnd(self, item):
        """ Return True if skip rest of code """
        self.mode = MODE_NOOP

        if isinstance(item, NodeEditorGraphicsSocket):
            if item.socket != self.lastStartSocket:
                printDebug(DEBUG, f'previous edge: {self.previousEdge}')
                if item.socket.hasEdge(): item.socket.edge.remove()
                printDebug(DEBUG, f'assign end socket: {item.socket}')
                if self.previousEdge: self.previousEdge.remove()
                printDebug(DEBUG, 'previous edge removed')
                self.dragEdge.startSocket = self.lastStartSocket
                self.dragEdge.endSocket = item.socket
                self.dragEdge.startSocket.setConnectedEdge(self.dragEdge)
                self.dragEdge.endSocket.setConnectedEdge(self.dragEdge)
                printDebug(DEBUG, f'reassigned start and send socket to drag edge')
                self.dragEdge.updatePositions()
                return True

        printDebug(DEBUG, 'end dragging edge')
        self.dragEdge.remove()
        self.dragEdge = None
        printDebug(DEBUG, f'about to set socket to previous edge: {self.previousEdge}')
        if not self.previousEdge:
            self.previousEdge.startSocket.edge = self.previousEdge
        printDebug(DEBUG, 'everything done')

        return False
    
    def distanceBetweenClickAndReleaseIsOff(self, event):
        
        newLMBReleaseScenePos = self.mapToScene(event.pos())
        distScene = newLMBReleaseScenePos - self.lastLMBClickScenePos
        edgeDragThresholdSq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD

        return (distScene.x()*distScene.x() + distScene.y()*distScene.y()) > edgeDragThresholdSq

    def deleteSelected(self):
        for item in self.graphicsScene.selectedItems():
            if isinstance(item, NodeEditorGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

    def cutIntersectingEdges(self):

        for i in range(len(self.cutLine.linePoints) - 1):
            p1 = self.cutLine.linePoints[i]
            p2 = self.cutLine.linePoints[i + 1]
            
            for edge in self.graphicsScene.scene.edges:
                if edge.graphicsEdge.intersectsWith(p1, p2):
                    edge.remove()


class NodeEditorQGraphScene(QGraphicsScene):

    def __init__(self, scene, parent=None):
        super(NodeEditorQGraphScene, self).__init__(parent)

        self.scene = scene

        # Settings
        self.gridSize = 20
        self.gridSquaares = 5

        self.backgroundColor = QColor('#262630')
        self.gridColor1 = QColor('#1A1A20')
        self.gridColor2 = QColor('#121212')

        self.gridPen1 = QPen(self.gridColor2)
        self.gridPen1.setWidth(2)

        self.gridPen2 = QPen(self.gridColor1)
        self.gridPen2.setWidth(1)

        self.setBackgroundBrush(self.backgroundColor)
    
    def setGraphicsScene(self, width, height):
        self.setSceneRect(-width//2, -height//2, width, height)
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left   = int(math.floor(rect.left()))
        right  = int(math.ceil(rect.right()))
        top    = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        firstLeft = left - (left % self.gridSize)
        firstTop  = top - (top % self.gridSize)
        
        gridLines1, gridLines2 = [], []
        for x in range(firstLeft, right, self.gridSize):
            if (x % (self.gridSize * self.gridSquaares) == 0): 
                gridLines1.append(QLine(x, top, x, bottom))
            else: gridLines2.append(QLine(x, top, x, bottom))

        for y in range(firstTop, bottom, self.gridSize):
            if (y % (self.gridSize * self.gridSquaares) == 0): 
                gridLines1.append(QLine(left, y, right, y))
            else: gridLines2.append(QLine(left, y, right, y))

        painter.setPen(self.gridPen1)
        painter.drawLines(gridLines1)

        painter.setPen(self.gridPen2)
        painter.drawLines(gridLines2)


class NodeEditorScene():
    def __init__(self):
        
        self.nodes = []
        self.edges = []

        self.sceneW, self.sceneH = 50000, 50000

        self.graphicsScene = NodeEditorQGraphScene(self)
        self.graphicsScene.setGraphicsScene(self.sceneW, self.sceneH)
        
    def addNode(self, node):
        self.nodes.append(node)
    
    def addEdge(self, edge):
        self.edges.append(edge)
    
    def removeNode(self, node):
        self.nodes.remove(node)
    
    def removeEdge(self, edge):
        self.edges.remove(edge)


class NodeEditorNode():
    
    def __init__(self, scene, title='Undefined Node', inputs=[], outputs=[]):

        self.scene = scene
        self.title = title

        self.spacing = 20

        self.content = NodeEditorContentQWidget(self)

        self.graphicsNode = NodeEditorGraphicsNode(self)

        self.scene.addNode(self)
        self.scene.graphicsScene.addItem(self.graphicsNode)

        self.inputs  = []
        self.outputs = []
        
        for i, socket in enumerate(inputs):
            socket = NodeEditorSocket(node=self, index=i, position=LEFT_TOP, socketType=socket)
            self.inputs.append(socket)
        
        for i, socket in enumerate(outputs):
            socket = NodeEditorSocket(node=self, index=i, position=RIGHT_TOP, socketType=socket)
            self.outputs.append(socket)
    
    def __str__(self):
        return '<%s %s..%s>' % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
    
    @property
    def position(self):
        return self.graphicsNode.pos()

    def setPosition(self, x, y):

        self.graphicsNode.setPos(x, y)
    
    def getSocketPosition(self, index, position):

        x = 0 if position == LEFT_TOP or position == LEFT_BOTTOM else self.graphicsNode.width

        if position == LEFT_BOTTOM or position == RIGHT_BOTTOM:
            y = self.graphicsNode.height - self.graphicsNode.edgeSize - self.graphicsNode._padding - index * self.spacing 
        else:
            y = self.graphicsNode.titleHeight + self.graphicsNode._padding + self.graphicsNode.edgeSize + index * self.spacing

        return [x, y]
    
    def updateConnectedEdges(self):

        for socket in self.inputs + self.outputs:
            if socket.hasEdge():
                socket.edge.updatePositions()

    def remove(self):
        printDebug(DEBUG, f'> Removing node: {self}')
        printDebug(DEBUG, ' - Remove all edges from sockets')
        for socket in (self.inputs + self.outputs):
            if socket.hasEdge():
                printDebug(DEBUG, f'    - removing from socket: {socket} - removing edge: {socket.edge}')
                socket.edge.remove()
        printDebug(DEBUG, ' - Remove NodeEditorGraphicsNode')
        self.scene.graphicsScene.removeItem(self.graphicsNode)
        self.graphicsNode = None
        printDebug(DEBUG, ' - Remove node from the scene')
        self.scene.removeNode(self)
        printDebug(DEBUG, ' - Everything is done')


class NodeEditorGraphicsNode(QGraphicsItem):
    
    def __init__(self, node, parent=None):
        super(NodeEditorGraphicsNode, self).__init__(parent)

        self.node = node
        self.content = self.node.content

        self._titleColor = Qt.white
        self._titleFont = QFont('times new roman', 10)

        self.width, self.height = 180, 240
        self.titleHeight = 24
        self.edgeSize = 10
        self._padding = 10.0

        self._penDefault = QPen(QColor('#7F000000'))
        self._penSelected = QPen(QColor('#FFFFA637'))

        self._brushTitle = QBrush(QColor('#FF313131'))
        self._brushBackground = QBrush(QColor('#E3212121'))

        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemIsMovable)

        self.setTitle()

        #... init sockets
        self.initializeSockets()

        #... init content
        self.graphicsContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edgeSize, self.titleHeight + self.edgeSize, self.width - 2*self.edgeSize, 
                                 self.height - 2*self.edgeSize-self.titleHeight)
        
        self.graphicsContent.setWidget(self.content)

        self.title = self.node.title

    def __str__(self):
        return '<%s %s..%s>' % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        #... NEEDS OPTIMIZATION! JUST UPDATE SELECTED NODES
        for node in self.scene().scene.nodes:
            if node.graphicsNode.isSelected():
                node.updateConnectedEdges()

    def setTitle(self):
        self.titleItem = QGraphicsTextItem(self)
        self.titleItem.node = self.node
        self.titleItem.setFont(self._titleFont)
        self.titleItem.setDefaultTextColor(self._titleColor)
        self.titleItem.setPos(self._padding, 0)
        self.titleItem.setTextWidth(self.width * 2 - self._padding)
    
    def initializeSockets(self):
        pass

    def boundingRect(self):
        return QRectF(0, 
                      0, 
                      self.width, 
                      self.height).normalized()
    
    def paint(self, painter, option, widget):
        
        #... Title 
        pathTitle = QPainterPath()
        pathTitle.setFillRule(Qt.WindingFill)
        pathTitle.addRoundedRect(0, 0, self.width, self.titleHeight, self.edgeSize, self.edgeSize)
        pathTitle.addRect(0, self.titleHeight - self.edgeSize, self.edgeSize, self.edgeSize)
        pathTitle.addRect(self.width - self.edgeSize, self.titleHeight - self.edgeSize, self.edgeSize, self.edgeSize)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brushTitle)
        painter.drawPath(pathTitle.simplified())

        #... Background
        pathBackground = QPainterPath()
        pathBackground.setFillRule(Qt.WindingFill)
        pathBackground.addRoundedRect(0, self.titleHeight, self.width, self.height - self.titleHeight, self.edgeSize, self.edgeSize)
        pathBackground.addRect(0, self.titleHeight, self.edgeSize, self.edgeSize)
        pathBackground.addRect(self.width - self.edgeSize, self.titleHeight, self.edgeSize, self.edgeSize)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brushBackground)
        painter.drawPath(pathBackground.simplified())

        #... Outline
        pathOutline = QPainterPath()
        pathOutline.addRoundedRect(0, 0, self.width, self.height,
                                   self.edgeSize, self.edgeSize)
        painter.setPen(self._penDefault if not self.isSelected() else self._penSelected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(pathOutline.simplified())
    
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.titleItem.setPlainText(self._title)


class NodeEditorContentQWidget(QWidget):
    
    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.labelWidget = QLabel("Some title")
        self.layout.addWidget(self.labelWidget)
        self.layout.addWidget(NodeEditorQTextEdit('foo'))
    
    def setEditingFlag(self, value):
        self.node.scene.graphicsScene.views()[0].ediitingFlag = value


class NodeEditorQTextEdit(QTextEdit):

    def focusInEvent(self, event):

        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):

        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)


class NodeEditorSocket():
    
    def __init__(self, node, index=0, position=LEFT_TOP, socketType=1):
        
        self.node = node
        self.index = index
        self.position = position
        self.socketType = socketType

        self.graphicsSocket = NodeEditorGraphicsSocket(self, self.socketType)

        self.graphicsSocket.setPos(*self.node.getSocketPosition(index, position))

        self.edge = None

    def __str__(self):
        return '<%s %s..%s>' % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
    
    def getSocketPosition(self):

        return self.node.getSocketPosition(self.index, self.position)

    def setConnectedEdge(self, edge=None):

        self.edge = edge

    def hasEdge(self):

        return self.edge


class NodeEditorGraphicsSocket(QGraphicsItem):

    def __init__(self, socket, socketType=1):
        super(NodeEditorGraphicsSocket, self).__init__(socket.node.graphicsNode)

        self.socket = socket
        self.socketType = socketType

        self._colors = [QColor('#FFFF7700'),
                        QColor('#FF528220'),
                        QColor('#FF0025e6'),
                        QColor('#FFa86db1'),
                        QColor('#FFb54747'),
                        QColor('#FFdbe220')]

        self.radius = 6.0
        self._widthOutline = 1.0
        self._colorBackground = self._colors[self.socketType]
        self._colorOutline = self._colors[self.socketType]

        self._pen = QPen(self._colorOutline)
        self._pen.setWidthF(self._widthOutline)
        self._brush = QBrush(self._colorBackground)

    def __str__(self):
        return '<%s %s..%s>' % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
    
    def paint(self, painter, option, widget):
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
    
    def boundingRect(self):
        return QRectF(-self.radius,
                      -self._widthOutline,
                      2*(self.radius + self._widthOutline),
                      2*(self.radius + self._widthOutline))


class NodeEditorEdge():

    def __init__(self, scene, startSocket, endSocket, edgeType=EDGE_TYPE_DIRECT):
        
        self.scene = scene

        self.startSocket = startSocket
        self.endSocket = endSocket

        self.startSocket.edge = self
        if self.endSocket:
            self.endSocket.edge = self

        self.graphicsEdge = NodeEditorEdgeDirect(self) if edgeType == EDGE_TYPE_DIRECT else NodeEditorEdgeBezier(self)

        self.updatePositions()

        self.scene.graphicsScene.addItem(self.graphicsEdge)
        self.scene.addEdge(self)

    def __str__(self):
        return '<%s %s..%s>' % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])

    def updatePositions(self):

        sourcePos = self.startSocket.getSocketPosition()
        sourcePos[0] += self.startSocket.node.graphicsNode.pos().x()
        sourcePos[1] += self.startSocket.node.graphicsNode.pos().y()
        self.graphicsEdge.setSource(*sourcePos)
        if self.endSocket:
            endPos = self.endSocket.getSocketPosition()
            endPos[0] += self.endSocket.node.graphicsNode.pos().x()
            endPos[1] += self.endSocket.node.graphicsNode.pos().y()
            self.graphicsEdge.setDestination(*endPos)
        else:
            self.graphicsEdge.setDestination(*sourcePos)
        self.graphicsEdge.update()
    
    def removeFromSocket(self):

        if self.startSocket: self.startSocket.edge = None
        if self.endSocket: self.endSocket.edge = None

        self.startSocket = None
        self.endSocket = None
    
    def remove(self):
        printDebug(DEBUG, f'> Remvoing Edge: {self}')
        printDebug(DEBUG, ' - Remove edge from all sockets')
        self.removeFromSocket()
        printDebug(DEBUG, ' - Remove NodeEditorGraphicsEdge from scene')
        self.scene.graphicsScene.removeItem(self.graphicsEdge)
        self.graphicsEdge = None
        printDebug(DEBUG, ' - Remove edge from scene')
        try:
            self.scene.removeEdge(self)
        except  ValueError:
            pass
        printDebug(DEBUG, ' - Everything is done')


class NodeEditorGraphicsEdge(QGraphicsPathItem):
    """
    Represents a graphics edge in the node editor.

    Args:
        edge: The edge object associated with this graphics edge.
        parent: The parent item of this graphics edge.

    Attributes:
        _color: The color of the edge.
        _colorSelected: The color of the edge when selected.
        _pen: The pen used to draw the edge.
        _penSelected: The pen used to draw the edge when selected.
        _penDragging: The pen used to draw the edge when dragging.
        posSource: The source position of the edge.
        posDestination: The destination position of the edge.
    """

    def __init__(self, edge, parent=None):
        super(NodeEditorGraphicsEdge, self).__init__(parent)

        self.edge = edge

        self._color = QColor('#001000')
        self._colorSelected = QColor('#00ff00')

        self._pen = QPen(self._color)
        self._pen.setWidth(2.0)
        self._penSelected = QPen(self._colorSelected)
        self._penSelected.setWidth(2.0)
        self._penDragging = QPen(self._color)
        self._penDragging.setWidth(2.0)
        self._penDragging.setStyle(Qt.DashLine)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setZValue(-1)

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    def paint(self, painter, option, widget):
        """
        Paints the graphics edge.

        Args:
            painter: The QPainter object used for painting.
            option: The style options for painting.
            widget: The widget being painted on.
        """
        self.setPath(self.calcPath())

        if not self.edge.endSocket:
            painter.setPen(self._penDragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._penSelected)

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def calcPath(self):
        """
        Calculates the path of the graphics edge.

        Returns:
            The QPainterPath representing the path of the edge.
        """
        raise NotImplemented('This method has to be overwritten in a child class')

    def intersectsWith(self, p1, p2):
        """
        Checks if the graphics edge intersects with a line segment.

        Args:
            p1: The start point of the line segment.
            p2: The end point of the line segment.

        Returns:
            True if the edge intersects with the line segment, False otherwise.
        """
        cutPath = QPainterPath(p1)
        cutPath.lineTo(p2)

        path = self.calcPath()

        return cutPath.intersects(path)
    

class NodeEditorEdgeDirect(NodeEditorGraphicsEdge):
    """
    Represents a direct edge in the node editor.

    This class inherits from NodeEditorGraphicsEdge and provides
    functionality to calculate the path of the edge.

    Attributes:
        posSource (tuple): The position of the source node.
        posDestination (tuple): The position of the destination node.
    """

    def calcPath(self):
        """
        Calculate the path of the edge.

        Returns:
            QPainterPath: The calculated path of the edge.
        """
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])

        return path

class NodeEditorEdgeBezier(NodeEditorGraphicsEdge):
    """
    Represents a Bezier curve edge in the node editor.

    This class calculates the path of the Bezier curve based on the source and destination positions,
    and provides a method to retrieve the calculated path.

    Attributes:
        posSource (tuple): The position of the source node.
        posDestination (tuple): The position of the destination node.
        edge (NodeEditorGraphicsEdge): The edge object associated with this Bezier curve.
    """

    def calcPath(self):
        """
        Calculates the path of the Bezier curve based on the source and destination positions.

        Returns:
            QPainterPath: The calculated path of the Bezier curve.
        """
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpxS = +dist
        cpxD = -dist
        cpyS = 0
        cpyD = 0

        startSocketPos = self.edge.startSocket.position

        if (s[0] > d[0] and startSocketPos in (RIGHT_TOP, RIGHT_BOTTOM)) or (s[0] < d[0] and startSocketPos in (LEFT_TOP, LEFT_BOTTOM)):
            cpxD *= -1 
            cpxS *= -1

            cpyD = ((s[1]-d[1]) / abs(s[1]-d[1] or 0.000001)) * EDGE_CP_ROUNDNESS
            cpyS = ((d[1]-s[1]) / abs(d[1]-s[1] or 0.000001)) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0]+cpxS, s[1]+cpyS, d[0]+cpxD, d[1]+cpyD, self.posDestination[0], self.posDestination[1])
        
        return path


class NodeEditorGraphicsCutline(QGraphicsItem):
    """
    A graphics item representing a cutline in the node editor.

    Attributes:
        linePoints (list): The points defining the cutline.
        _pen (QPen): The pen used for drawing the cutline.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.linePoints = []

        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)
    
    def boundingRect(self):
        return QRectF(0, 0, 1, 1)
    
    def paint(self, painter, option, widget):
        """
        Paints the cutline on the graphics item.

        Args:
            painter (QPainter): The painter object used for drawing.
            option (QStyleOptionGraphicsItem): Style options for the item.
            widget (QWidget): The widget being painted on.
        """
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        polyLine = QPolygonF(self.linePoints)
        painter.drawPolyline(polyLine)






























