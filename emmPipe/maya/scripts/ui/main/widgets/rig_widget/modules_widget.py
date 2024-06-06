
import maya.cmds as cmds

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtGui import QFont

from controller.meta_data.query import MetaDataQuery
from ui.ui_utils import DockableUI, CollapsibleWidget, set_stylesheet

from rig.objects.object_data import DependencyNodeData
from rig.skeleton_creator.skeleton_creator import SkeletonCreator, SkeletonBase


class ModulesWidget(DockableUI):

    WINDOW_TITLE = 'Skeleton UI'

    WINDOW_HEIGHT = 1000
    WINDOW_WIDTH = 350

    def __init__(self):
        super().__init__()

        self.meta_node = None

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        set_stylesheet(self, 'VisualScript')

    def add_widgets(self):

        self.coll_widget = CollapsibleWidget('Create skeleton module')
        self.coll_widget.body_widget.setFixedHeight(280)
        self.coll_widget.body_widget.setFixedWidth(320)

        self.skeleton_creator_widget = SkeletonCreatorWidget(self.coll_widget)
        self.skeleton_creator_widget.setFixedWidth(self.coll_widget.body_widget.width())
        self.skeleton_creator_widget.setFixedHeight(self.coll_widget.body_widget.height())

        self.side_combo_box = QtWidgets.QComboBox()
        self.side_combo_box.addItems(['Center', 'Left', 'Right'])
        
        self.list_widget = QtWidgets.QListWidget()
        list_font = QFont()
        
        list_font.setPointSize(12)
        list_font.setFamily('Arial')
        self.list_widget.setFixedHeight(200)
        self.list_widget.setFont(list_font)

        for item in MetaDataQuery.skeleton_creator():

            self.list_widget.addItem(item.replace('_metaData', ''))

        self.module_info_widget = SkeletonModuleInfoWidget()

        return

    def add_layouts(self):
        
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.coll_widget.body_layout.addWidget(self.skeleton_creator_widget)

        self.list_widget_settings_layout = QtWidgets.QHBoxLayout()
        self.list_widget_settings_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.list_widget_settings_layout.addWidget(QtWidgets.QLabel('Side:'))
        self.list_widget_settings_layout.addWidget(self.side_combo_box)
        
        layout.addWidget(self.coll_widget)
        layout.addLayout(self.list_widget_settings_layout)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.module_info_widget)

        layout.addStretch()    
        self.setLayout(layout)

        return

    def add_connections(self):
        
        self.list_widget.itemClicked.connect(self.set_meta_node)
        self.list_widget.itemClicked.connect(self.select_module)

        return

    def set_meta_node(self):

        self.meta_node = DependencyNodeData(f'{self.list_widget.currentItem().text()}_metaData')

        return

    def select_module(self):

        cmds.select(self.meta_node.get_connected_nodes(self.meta_node.get_plug('__module')))
        self.module_info_widget.set_module(self.meta_node)
    
    def select_joints(self):

        cmds.select(self.meta_node.get_connected_nodes(self.meta_node.get_plug('__joints')))

class SkeletonCreatorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        return

    def add_widgets(self):

        self.skeleton_base_button = QtWidgets.QPushButton('Skeleton Base')
        if MetaDataQuery.skeleton_base():
            self.skeleton_base_button.setEnabled(False)

        self.name_line_edit = QtWidgets.QLineEdit()
        self.name_line_edit.setPlaceholderText('Name')

        self.side_combo_box = QtWidgets.QComboBox()
        self.side_combo_box.addItems(['Center', 'Left', 'Right'])

        self.index_spin_box = QtWidgets.QSpinBox()
        self.index_spin_box.setRange(0, 100)
        self.index_spin_box.setValue(0)

        self.num_joints_spin_box = QtWidgets.QSpinBox()
        self.num_joints_spin_box.setRange(1, 100)
        self.num_joints_spin_box.setValue(1)

        self.parent_combo_box = QtWidgets.QComboBox()
        self.parent_combo_box.addItems([item.replace('_metaData','') for item in MetaDataQuery.skeleton_creator()])

        self.up_type_combo_box = QtWidgets.QComboBox()
        self.up_type_combo_box.addItems(['None', 'Object', 'Vector Plane'])

        self.hook_idx_spin_box = QtWidgets.QSpinBox()
        self.hook_idx_spin_box.setRange(0, 100)
        self.hook_idx_spin_box.setValue(0)

        self.replace_hook_check_box = QtWidgets.QCheckBox('Replace Hook')

        self.create_button = QtWidgets.QPushButton('Create')

        return

    def add_layouts(self):
        
        self.layout = QtWidgets.QFormLayout()
        self.layout.setLabelAlignment(QtCore.Qt.AlignLeft)

        self.layout.addRow(self.skeleton_base_button)
        self.layout.addRow('Name:', self.name_line_edit)
        self.layout.addRow('Side:', self.side_combo_box)
        self.layout.addRow('Index:', self.index_spin_box)
        self.layout.addRow('# of Joints:', self.num_joints_spin_box)
        self.layout.addRow('Parent:', self.parent_combo_box)
        self.layout.addRow('Up Type:', self.up_type_combo_box)
        self.layout.addRow('Hook Index:', self.hook_idx_spin_box)
        self.layout.addRow('Replace Hook:', self.replace_hook_check_box)
        self.layout.addRow(self.create_button)

        self.setLayout(self.layout)

        return

    def add_connections(self):
    
        self.skeleton_base_button.clicked.connect(self.create_base_module)
        self.create_button.clicked.connect(self.create_module)

        return
    
    def reset_fields(self):
            
            self.name_line_edit.clear()
            self.name_line_edit.setPlaceholderText('Name')
            self.side_combo_box.setCurrentIndex(0)
            self.index_spin_box.setValue(0)
            self.num_joints_spin_box.setValue(1)
            self.parent_combo_box.clear()
            self.parent_combo_box.addItems([item.replace('_metaData','') for item in MetaDataQuery.skeleton_creator()])
            self.parent_combo_box.setCurrentIndex(0)
            self.up_type_combo_box.setCurrentIndex(0)
            self.hook_idx_spin_box.setValue(0)
            self.replace_hook_check_box.setChecked(False)
    
            return
    
    def create_base_module(self):

        SkeletonBase().create()

        self.skeleton_base_button.setEnabled(False)

        return
    
    def create_module(self):

        name = self.name_line_edit.text().lower()
        side = 'l' if self.name_line_edit.text() == 'Left' else 'r' if self.name_line_edit.text() == 'Right' else 'c'
        desc = 'skeleton'
        index = self.index_spin_box.value()
        num_joints = self.num_joints_spin_box.value()
        parent = self.parent_combo_box.currentText()
        up_type = None if self.up_type_combo_box.currentText() == 'None' else self.up_type_combo_box.currentText()
        hook_idx = self.hook_idx_spin_box.value()
        replace_hook = self.replace_hook_check_box.isChecked()

        SkeletonCreator(name, side, desc, index, num_joints, 
                        parent, up_type, hook_idx, 
                        replace_hook).create()
        
        self.reset_fields()

        return
    

class SkeletonModuleInfoWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        return

    def add_widgets(self):

        self.name_label = QtWidgets.QLabel('Name:')
        self.name_value = QtWidgets.QLabel()

        self.side_label = QtWidgets.QLabel('Side:')
        self.side_value = QtWidgets.QLabel()

        self.index_label = QtWidgets.QLabel('Index:')
        self.index_value = QtWidgets.QLabel()

        self.num_joints_label = QtWidgets.QLabel('# of Joints:')
        self.num_joints_value = QtWidgets.QLabel()

        self.parent_label = QtWidgets.QLabel('Parent:')
        self.parent_value = QtWidgets.QLabel()

        self.up_type_label = QtWidgets.QLabel('Up Type:')
        self.up_type_value = QtWidgets.QLabel()

        self.hook_idx_label = QtWidgets.QLabel('Hook Index:')
        self.hook_idx_value = QtWidgets.QLabel()

        self.replace_hook_label = QtWidgets.QLabel('Replace Hook:')
        self.replace_hook_value = QtWidgets.QLabel()

        return

    def add_layouts(self):

        self.layout = QtWidgets.QFormLayout()
        self.layout.setLabelAlignment(QtCore.Qt.AlignLeft)

        self.layout.addRow(self.name_label, self.name_value)
        self.layout.addRow(self.side_label, self.side_value)
        self.layout.addRow(self.index_label, self.index_value)
        self.layout.addRow(self.num_joints_label, self.num_joints_value)
        self.layout.addRow(self.parent_label, self.parent_value)
        self.layout.addRow(self.up_type_label, self.up_type_value)
        self.layout.addRow(self.hook_idx_label, self.hook_idx_value)
        self.layout.addRow(self.replace_hook_label, self.replace_hook_value)

        self.setLayout(self.layout)

        return

    def add_connections(self):

        return

    def set_module(self, meta_node):
        """
        Sets the values of the module widget based on the provided module object.

        Args:
            module (Module): The module object containing the data to be displayed.

        Returns:
            None
        """
        #self.name_value.setText(meta_node.name)
        self.side_value.setText(meta_node.side)
        self.index_value.setText(str(meta_node.index))
        self.num_joints_value.setText(str(meta_node.num_joints))
        self.parent_value.setText(meta_node.parent)
        self.up_type_value.setText(meta_node.up_type)
        self.hook_idx_value.setText(str(meta_node.hook_idx))
        self.replace_hook_value.setText(str(meta_node.replace_hook))

        return
