import json

from PyQt5.QtGui import QFont, QColor
from qgis.PyQt.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QScrollArea, QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os
from qgis.gui import QgsColorButton

from new_category_element import NewCategoryElement

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "app_settings.ui"))


def update_colour(pad, colour):
    pad.colour = colour.name()


class AppSettingsDialog(QDialog, FORM_CLASS):
    def __init__(self, keypad_manager, attributes, parent=None):
        super(AppSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.keypad_manager = keypad_manager
        keypad_manager.create_data_copy()
        self.categoryListWidget.itemSelectionChanged.connect(self._on_category_item_selected)
        self.elementListWidget.itemSelectionChanged.connect(self._on_element_item_selected)
        self.selected_category = ''
        self.selected_element = ''
        self.colour = '#000000'
        self.font = f'normal 8pt "MS Shell Dlg 2"'
        self.height = 30
        self.width = 100
        self.attributes = None

        if attributes is not None:
            self.mFontButton.setCurrentFont(attributes["font"])
            self.mColorButton.setColor(QColor(attributes["colour"]))
            self.heightLineEdit.setText(f'{attributes["height"]}')
            self.widthLineEdit.setText(f'{attributes["width"]}')

        self.updated_settings = False
        self._clear_and_populate_categories()

        # Connect buttons to functions
        self.moveDownPadItemPushButton.clicked.connect(lambda :self.move_category("down"))
        self.moveUpPadItemPushButton.clicked.connect(lambda :self.move_category("up"))
        self.moveDownNeedleItemPushButton.clicked.connect(lambda: self.move_element("down"))
        self.moveUpNeedleItemPushButton.clicked.connect(lambda: self.move_element("up"))

        self.addCategoryPushButton.clicked.connect(lambda: self.open_add_dialog("category"))
        self.addElementPushButton.clicked.connect(lambda: self.open_add_dialog("element"))

        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        self.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.discard_settings)
        self.mFontButton.changed.connect(self._font_changed)
        self.mColorButton.colorChanged.connect(self._colour_changed)

    def move_category(self, direction):
        QgsApplication.messageLog().logMessage(f"move_category: {direction}", 'DigitalSketchPlugin')
        self.keypad_manager.move_category(self.selected_category,direction)
        self._clear_and_populate_categories()

    def move_element(self, direction):
        QgsApplication.messageLog().logMessage(f"move_element: {direction}", 'DigitalSketchPlugin')
        self.keypad_manager.move_item(self.selected_category, self.selected_element, direction)
        self._clear_populate_elements_list(self.selected_category)

    def checkbox_state_changed(self, checkbox, state):
        QgsApplication.messageLog().logMessage(f"checkbox {checkbox.objectName()} state_changed: {state}", 'DigitalSketchPlugin')
        self.keypad_manager.set_category_selection(checkbox.objectName(), state)

    def open_add_dialog(self, mode):
        QgsApplication.messageLog().logMessage(f"open_add_dialog {mode}", 'DigitalSketchPlugin')

        add_dialog = NewCategoryElement(mode)
        if add_dialog.exec_() == QDialog.Accepted:
            data = add_dialog.get_add_data()
            if data:
                QgsApplication.messageLog().logMessage(f"accepted data {data}", 'DigitalSketchPlugin')
                if mode == 'category':
                    self.keypad_manager.add_category(data)
                    self._clear_and_populate_categories()

                else:
                    self.keypad_manager.add_item(self.selected_category, data)
                    self._clear_populate_elements_list(self.selected_category)

    def apply_settings(self):
        QgsApplication.messageLog().logMessage("apply_settings", 'DigitalSketchPlugin')
        self.updated_settings = True
        self.attributes = dict(font=self.font, colour=self.colour,
                               height=float(self.heightLineEdit.text().strip()),
                               width=float(self.widthLineEdit.text().strip()))
        self.keypad_manager.update_dataset()
        self.accept()

    def discard_settings(self):
        QgsApplication.messageLog().logMessage("discard_settings", 'DigitalSketchPlugin')
        self.updated_settings = False
        self.reject()

    def get_attributes(self):
        return self.attributes

    def _clear_and_populate_categories(self):
        self.categoryListWidget.clear()
        for pad in self.keypad_manager.data_cpy:
            QgsApplication.messageLog().logMessage(f"pad_item: {pad.category}", 'DigitalSketchPlugin')
            item = QListWidgetItem(self.categoryListWidget)
            widget = QWidget()
            layout = QHBoxLayout()

            # Colour Picker (QgsColorButton)
            colour_picker = QgsColorButton()
            colour_picker.setObjectName(pad.category)
            colour_picker.setColor(QColor(pad.colour))
            colour_picker.setMinimumSize(50, 30)  # Small size
            colour_picker.setMaximumSize(50, 30)  # Small size
            colour_picker.colorChanged.connect(lambda colour, p=pad: update_colour(p, colour))

            # Delete Button (QPushButton)
            delete_button = QPushButton('X')
            delete_button.setMaximumSize(30, 30)
            delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
            delete_button.clicked.connect(lambda: self.delete_keypad_item(item))

            c_box = QCheckBox(pad.category)
            c_box.setObjectName(pad.category)
            select_state = 2 if pad.selected == True else 0
            c_box.setCheckState(select_state)
            QgsApplication.messageLog().logMessage(
                f" {pad.category} {c_box.checkState()} is selected: {pad.selected}", 'DigitalSketchPlugin')
            c_box.stateChanged.connect(lambda state, cb=c_box: self.checkbox_state_changed(cb, state))

            layout.addWidget(c_box)
            layout.addWidget(colour_picker)
            layout.addWidget(delete_button)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(5)
            widget.setLayout(layout)

            item.setSizeHint(widget.sizeHint())
            self.categoryListWidget.setItemWidget(item, widget)

    def _on_category_item_selected(self):
        selected_items = self.categoryListWidget.selectedItems()
        if selected_items:
            item = selected_items[0]  # Get the first selected item
            widget = self.categoryListWidget.itemWidget(item)  # Get the widget inside

            if widget:
                c_box = widget.findChild(QCheckBox)  # Find the checkbox inside the widget
                if c_box:
                    self.selected_category = c_box.text()
                    QgsApplication.messageLog().logMessage(f"Selected Item: {c_box.text()}, Checked: {c_box.isChecked()}", 'DigitalSketchPlugin')
                    self.padItemsGroupBox.setTitle(f'Keypad: {c_box.text()}')
                    self._clear_populate_elements_list(c_box.text())

    def _clear_populate_elements_list(self, category_name):
        self.elementListWidget.clear()
        category = next((cat for cat in self.keypad_manager.data_cpy if cat.category == category_name), None)
        if category:
            for element in category.items:
                QgsApplication.messageLog().logMessage(f"pad_item: {element}", 'DigitalSketchPlugin')
                item = QListWidgetItem(self.elementListWidget)
                widget = QWidget()
                layout = QHBoxLayout()
                label = QLabel(element)
                label.setMinimumSize(50, 30)

                space = QSpacerItem(40, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)

                # edit Button (QPushButton)
                edit_button = QPushButton('Edit')
                edit_button.setMinimumSize(40, 30)
                edit_button.setMaximumSize(40, 30)
                edit_button.setStyleSheet("background-color: blue; color: white; border-radius: 5px;")
                edit_button.clicked.connect(lambda: self.delete_keypad_item(item))

                # Delete Button (QPushButton)
                delete_button = QPushButton('X')
                delete_button.setMinimumSize(30, 30)
                delete_button.setMaximumSize(30, 30)
                delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
                delete_button.clicked.connect(lambda: self.delete_keypad_item(item))

                layout.addWidget(label)
                layout.addItem(space)
                layout.addWidget(edit_button)
                layout.addWidget(delete_button)
                layout.setContentsMargins(2, 2, 2, 2)
                layout.setSpacing(5)
                widget.setLayout(layout)

                item.setSizeHint(widget.sizeHint())
                self.elementListWidget.setItemWidget(item, widget)

    def _on_element_item_selected(self):
        QgsApplication.messageLog().logMessage(f"_on_element_item_selected", 'DigitalSketchPlugin')
        selected_items = self.elementListWidget.selectedItems()
        if selected_items:
            item = selected_items[0]  # Get the first selected item
            widget = self.elementListWidget.itemWidget(item)  # Get the widget inside

            if widget:
                label = widget.findChild(QLabel)  # Find the checkbox inside the widget
                if label:
                    self.selected_element = label.text()
                    QgsApplication.messageLog().logMessage(f"Selected Item: {label.text()}", 'DigitalSketchPlugin')

    def _colour_changed(self, colour):
        self.colour = colour.name()
        QgsApplication.messageLog().logMessage(f'Colour: {self.colour}', 'DigitalSketchPlugin')

    def _font_changed(self):
        self.font = self.mFontButton.currentFont()
        QgsApplication.messageLog().logMessage("Font updated", 'DigitalSketchPlugin')