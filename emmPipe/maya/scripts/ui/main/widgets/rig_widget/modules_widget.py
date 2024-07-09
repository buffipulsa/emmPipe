
import maya.api.OpenMaya as om
import maya.cmds as cmds

from functools import partial

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

    def add_widgets(self):

        self.skel_creator_coll_widget = CollapsibleWidget('Create skeleton module')
        self.skel_creator_widget = SkeletonCreatorWidget()

        self.modules_coll_widget = CollapsibleWidget('Scene modules')
        self.modules_widget = SkeletonModuleWidget()

        self.skel_creator_coll_widget.scroll_area.setWidget(self.skel_creator_widget)
        self.modules_coll_widget.scroll_area.setWidget(self.modules_widget)

        return

    def add_layouts(self):
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        layout.addWidget(self.skel_creator_coll_widget)
        layout.addWidget(self.modules_coll_widget)
        layout.addStretch()

        return

    def add_connections(self):

        self.modules_widget.modules_list_widget.itemClicked.connect(self.select_module)

        self.skel_creator_widget.add_connections()
        self.modules_widget.add_connections()

        return

    def set_meta_node(self):

        self.meta_node = DependencyNodeData(f'{self.modules_widget.modules_list_widget.currentItem().text()}_metaData')
        self.modules_widget.meta_node = self.meta_node

        return

    def select_module(self):
        self.modules_widget.clear_module()
        self.set_meta_node()
        cmds.select(self.meta_node.get_connected_nodes(self.meta_node.get_plug('__module')))
        self.modules_widget.set_module()


class SkeletonCreatorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_widgets()
        self.add_layouts()

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
        self.layout.addRow(self.skeleton_base_button)
        self.layout.addRow('Name:', self.name_line_edit)
        self.layout.addRow('Side:', self.side_combo_box)
        self.layout.addRow('Index:', self.index_spin_box)
        self.layout.addRow('Joints:', self.num_joints_spin_box)
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

class SkeletonModuleWidget(QtWidgets.QWidget):
    
        def __init__(self, parent=None):
            super().__init__(parent)
    
            self.add_widgets()
            self.add_layouts()

            self.row_data = {}

            return
    
        def add_widgets(self):

            self.side_label = QtWidgets.QLabel('Side:')

            self.side_combo_box = QtWidgets.QComboBox()
            self.side_combo_box.addItems(['Center', 'Left', 'Right'])
            
            self.modules_list_widget = QtWidgets.QListWidget()
            list_font = QFont()
            list_font.setPointSize(12)
            list_font.setFamily('Arial')
            self.modules_list_widget.setFont(list_font)

            for item in MetaDataQuery.skeleton_creator():

                self.modules_list_widget.addItem(item.replace('_metaData', ''))

            self.module_data_label = QtWidgets.QLabel('Module Data')
        
            self.data_picker = QtWidgets.QComboBox()
            self.data_picker.addItems(['All', 'Modules', 'Joints', 'Controls', 'Utils'])

            self.data_list_widget = QtWidgets.QListWidget()
            list_font = QFont()
            list_font.setPointSize(12)
            list_font.setFamily('Arial')
            self.data_list_widget.setFont(list_font)
    
            return
    
        def add_layouts(self):
            
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)

            setting_layout = QtWidgets.QHBoxLayout()
            setting_layout.addWidget(self.side_label)
            setting_layout.addWidget(self.side_combo_box)
            setting_layout.addStretch()

            top_layout = QtWidgets.QHBoxLayout()
            top_layout.addWidget(self.module_data_label)
            top_layout.addWidget(self.data_picker)
            top_layout.addStretch()

            layout.addLayout(setting_layout)
            layout.addWidget(self.modules_list_widget)
            layout.addLayout(top_layout)
            layout.addWidget(self.data_list_widget)

            layout.addStretch()

            return
        
        def add_connections(self):

            self.data_picker.currentIndexChanged.connect(self.set_data_visibility)
            self.data_list_widget.itemClicked.connect(self.select_data)

            return
        
        def set_module(self):

            data = MetaDataQuery.meta_node_attrs_values(self.meta_node.dependnode_fn.name())

            self.row_data.clear()
            for i, attr in enumerate(data.keys()):
                self.data_list_widget.addItem(attr.replace("__",""))

                self.row_data[attr] = {'widget_item': self.data_list_widget.item(i), 'value': data[attr]['data'][0], 'category': data[attr]['category']}
            
            self.set_data_visibility()

        def clear_module(self):

            self.data_list_widget.clear()

            return

        def set_data_visibility(self):

            for key in self.row_data.keys():
                if self.data_picker.currentText() == 'All':
                    self.row_data[key]['widget_item'].setHidden(False)
                else:
                    if self.row_data[key]['category'] == self.data_picker.currentText().lower():
                        self.row_data[key]['widget_item'].setHidden(False)
                    else:
                        self.row_data[key]['widget_item'].setHidden(True)

        def select_data(self):

            sender = self.sender()
            sender_item = sender.item(sender.currentRow()).text()
            cmds.select(self.row_data[sender_item]['value'])

