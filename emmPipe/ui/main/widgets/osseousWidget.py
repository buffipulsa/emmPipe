import os

from PySide2 import QtWidgets
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout
from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2 import QtGui

import maya.cmds as cmds

from emmPipe.ui.ui_utils import CollapsibleWidget
from emmPipe.rig.osseous.osseous import Osseous

class OsseousWidget(QtWidgets.QWidget):

    ADD_PIXMAD = QtGui.QPixmap(':addClip.png')
    REMOVE_PIXMAD = QtGui.QPixmap(':removeRenderable.png')

    OK_PIXMAD = QtGui.QPixmap(':confirm.png')
    BROKEN_PIXMAD = QtGui.QPixmap(':caution.png')

    def __init__(self, parent=None):
        super().__init__(parent)

        self.d_module_data = {}

        self.add_widgets()
        self.add_layouts()
        self.add_connections()

        self.qslm_parent_names = QtCore.QStringListModel()
    
        self.osseous_widget.body_layout.insertLayout(0, self.module_layout())

    def add_widgets(self):
        
        self.osseous_widget = CollapsibleWidget('Osseous')

        self.build_button = QtWidgets.QPushButton('Build')

    def add_layouts(self):

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(self.osseous_widget)
        self.layout.addWidget(self.build_button)

    def add_connections(self):
        
        self.build_button.clicked.connect(self.build)

    def build(self):

        d_parent_data = {}

        for i in range(self.osseous_widget.body_layout.count()):
            layout = self.osseous_widget.body_layout.itemAt(i)
            if layout in self.d_module_data:
                name = layout.itemAt(2).widget().text()
                side = self.d_module_data[layout][3].currentText()
                num_joints = int(self.d_module_data[layout][4].text())
                parent = self.d_module_data[layout][5].currentText()
                print(parent)
                if parent in d_parent_data: parent = d_parent_data[parent]
                else:                       parent = None

                oss_module = Osseous()
                oss_module.name = name
                oss_module.side = side; 
                oss_module.num_joints = num_joints
                oss_module.parent = parent
                
                oss_module.create()

                d_parent_data[f'{name}({side})'] = oss_module
                print(d_parent_data)

    def module_layout(self):
        """
        Creates and returns a QHBoxLayout for the module layout.

        Returns:
            QHBoxLayout: The layout containing the module widgets.
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignLeft)

        add_button = QtWidgets.QPushButton()
        add_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.ADD_PIXMAD.scaled(10, 10)
        add_button.setIcon(self.ADD_PIXMAD)
        add_button.setFixedSize(self.ADD_PIXMAD.size())

        remove_button = QtWidgets.QPushButton()
        remove_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.REMOVE_PIXMAD.scaled(10, 10)
        remove_button.setIcon(self.REMOVE_PIXMAD)
        remove_button.setFixedSize(self.ADD_PIXMAD.size())

        name_lineedit = QtWidgets.QLineEdit()
        name_lineedit.setPlaceholderText('Name')
        name_lineedit.setFixedWidth(60)
        name_lineedit.setFocusPolicy(Qt.ClickFocus)

        side_combobox = QtWidgets.QComboBox()
        side_combobox.setFixedWidth(40)
        side_combobox.addItem('C')
        side_combobox.addItem('L')
        side_combobox.addItem('R')

        num_joints_lineedit = QtWidgets.QLineEdit('1')
        num_joints_lineedit.setFixedWidth(30)
        num_joints_lineedit.setAlignment(Qt.AlignRight)

        parent_combobox = QtWidgets.QComboBox()
        parent_combobox.setFixedWidth(60)

        status_label = QtWidgets.QLabel('a')
        status_label.setFixedWidth(self.OK_PIXMAD.width())
        status_label.setFixedHeight(self.OK_PIXMAD.height())
        status_label.setPixmap(self.OK_PIXMAD)
        #status_label.setStyleSheet(f'background-color: {self.LABEL_COLOR};

        layout.addWidget(add_button)
        layout.addWidget(remove_button)
        layout.addWidget(name_lineedit)
        layout.addWidget(side_combobox)
        layout.addWidget(num_joints_lineedit)
        layout.addWidget(parent_combobox)
        layout.addWidget(status_label)

        self.d_module_data[layout] = [add_button, remove_button, 
                                        name_lineedit, side_combobox, 
                                        num_joints_lineedit, parent_combobox]

        add_button.clicked.connect(self.on_add_clicked)
        remove_button.clicked.connect(self.on_remove_clicked)
        name_lineedit.editingFinished.connect(self.on_line_edit_changed)

        return layout

    def on_line_edit_changed(self):

        line_edit = self.sender()
        clicked_button_layout = self.retrive_layout_from_sender(line_edit, self.d_module_data)
        parent_index = self.osseous_widget.body_layout.indexOf(clicked_button_layout)

        self.qslm_parent_names.setData(self.qslm_parent_names.index(parent_index), 
                                        line_edit.text(),
                                        Qt.EditRole)

    def on_add_clicked(self):
        """
        Event handler for the 'add' button click.

        This method is called when the 'add' button is clicked. It retrieves the layout from the sender button,
        determines its parent index in the body layout, and inserts a new module layout at the next index.
        """
        clicked_button_layout = self.retrive_layout_from_sender(self.sender(), self.d_module_data)
        parent_index = self.osseous_widget.body_layout.indexOf(clicked_button_layout)
        new_layout = self.module_layout()
        self.osseous_widget.body_layout.insertLayout(parent_index+1, new_layout)

        l_parent_names = [] 
        for i in range(self.osseous_widget.body_layout.count() - 1):
            layout = self.osseous_widget.body_layout.itemAt(i)
            if layout in self.d_module_data:
                name = self.d_module_data[layout][2].text()
                if not name: name = f'Unnamed({clicked_button_layout.itemAt(3).widget().currentText()})'
                side = self.d_module_data[layout][3].currentText()
                l_parent_names.append(f'{name}({side})')
        
        self.qslm_parent_names.setStringList(l_parent_names)

        self.d_module_data[new_layout][5].clear()
        self.d_module_data[new_layout][5].setMaxVisibleItems(parent_index+1)
        self.d_module_data[new_layout][5].setModel(self.qslm_parent_names)

    def on_remove_clicked(self):
        """
        Event handler for the 'remove' button click.

        This method removes the clicked button layout and its associated widgets from the parent layout.
        """
        if len(self.d_module_data) > 1:
            clicked_button_layout = self.retrive_layout_from_sender(self.sender(), self.d_module_data)
            
            self.qslm_parent_names.removeRow(self.osseous_widget.body_layout.indexOf(clicked_button_layout))

            while clicked_button_layout.count():
                widget = clicked_button_layout.takeAt(0).widget()
                if widget: widget.deleteLater()

            if clicked_button_layout is not None:
                parent = clicked_button_layout.parent()
                if parent is not None:
                    parent.removeItem(clicked_button_layout)
                
                self.d_module_data.pop(clicked_button_layout)
                print(self.osseous_widget.body_layout.indexOf(clicked_button_layout))
                del clicked_button_layout

    def retrive_layout_from_sender(self, sender, d_module_data):
        """
        Retrieves the layout from the sender widget based on a dictionary.

        Args:
            sender: The widget from which to retrieve the layout.
            dict: A dictionary containing layouts and their associated widgets.

        Returns:
            The layout that contains the sender widget, or None if not found.
        """
        parent_layout = sender.parent().layout()

        for i in range(parent_layout.count()):
            layout = parent_layout.itemAt(i)
            if layout in d_module_data and sender in d_module_data[layout]:
                return layout

        return None
    
    

    # def update_model(self, text):
    #     # Split the text into individual items


    #     # Update the QStringListModel with the new list of items
    #     self.string_list_model.setStringList(items)


        

