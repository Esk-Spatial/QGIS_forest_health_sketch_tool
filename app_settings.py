
from PyQt5.QtGui import QColor
from qgis.PyQt.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QScrollArea, QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os
from qgis.gui import QgsColorButton

from edit_element import EditElement
from helper import show_delete_confirmation
from new_category_element import NewCategoryElement

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "app_settings.ui"))


def update_colour(pad, colour):
    pad.colour = colour.name()

def get_category_element(text):
    return text.split(':')

class AppSettingsDialog(QDialog, FORM_CLASS):
    def __init__(self, keypad_manager, attributes, parent=None):
        super(AppSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.keypad_manager = keypad_manager
        keypad_manager.create_data_copy()
        self.categoryListWidget.itemSelectionChanged.connect(self.on_category_item_selected)
        self.elementListWidget.itemSelectionChanged.connect(self.on_element_item_selected)
        self.selected_category = ''
        self.selected_element = ''
        self.folder_location = None
        self.colour = self.mColorButton.color().name(QColor.HexArgb)
        self.feature_colour = self.featureColorButton.color().name(QColor.HexArgb)
        self.font = self.mFontButton.currentFont()
        self.height = 30
        self.width = 150
        self.attributes = None

        if attributes is not None:
            self.folder_location = attributes["folder_path"]
            self.folderQgsFileWidget.setFilePath(attributes["folder_path"])
            self.change_folder_ctrl_to_readonly(attributes["folder_path"])
            self.featureColorButton.setColor(QColor(attributes["feature_colour"]))
            self.heightLineEdit.setText(attributes["surveyor"])
            self.heightLineEdit.setText(attributes["type_txt"])
            self.mFontButton.setCurrentFont(attributes["font"])
            self.mColorButton.setColor(QColor(attributes["colour"]))
            self.heightLineEdit.setText(f'{attributes["height"]}')
            self.widthLineEdit.setText(f'{attributes["width"]}')

        self.updated_settings = False
        self.clear_and_populate_categories()

        # Connect buttons to functions
        self.moveDownPadItemPushButton.clicked.connect(lambda :self.move_category("down"))
        self.moveUpPadItemPushButton.clicked.connect(lambda :self.move_category("up"))
        self.moveDownNeedleItemPushButton.clicked.connect(lambda: self.move_element("down"))
        self.moveUpNeedleItemPushButton.clicked.connect(lambda: self.move_element("up"))

        self.addCategoryPushButton.clicked.connect(lambda: self.open_add_dialog("category"))
        self.addElementPushButton.clicked.connect(lambda: self.open_add_dialog("element"))

        self.applyPushButton.clicked.connect(self.apply_settings)
        self.discardPushButton.clicked.connect(self.discard_settings)
        self.mFontButton.changed.connect(self.font_changed)
        self.featureColorButton.colorChanged.connect(self.feature_colour_changed)
        self.mColorButton.colorChanged.connect(self.colour_changed)
        self.folderQgsFileWidget.fileChanged.connect(self.set_folder_location)

    def move_category(self, direction):
        QgsApplication.messageLog().logMessage(f"move_category: {direction}", 'DigitalSketchPlugin')
        self.keypad_manager.move_category(self.selected_category,direction)
        self.clear_and_populate_categories()

    def move_element(self, direction):
        QgsApplication.messageLog().logMessage(f"move_element: {direction}", 'DigitalSketchPlugin')
        self.keypad_manager.move_item(self.selected_category, self.selected_element, direction)
        self.clear_populate_elements_list(self.selected_category)

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
                    self.clear_and_populate_categories()

                else:
                    self.keypad_manager.add_item(self.selected_category, data)
                    self.clear_populate_elements_list(self.selected_category)

    def apply_settings(self):
        QgsApplication.messageLog().logMessage("apply_settings", 'DigitalSketchPlugin')
        self.updated_settings = True
        self.attributes = dict(folder_path=self.folder_location, feature_colour=self.feature_colour,
                               surveyor=self.surveyourLineEdit.text().strip(), type_txt=self.typeLineEdit.text().strip(),
                               font=self.font, colour=self.colour, height=int(self.heightLineEdit.text().strip()),
                               width=int(self.widthLineEdit.text().strip()))
        self.keypad_manager.update_dataset()
        self.accept()

    def discard_settings(self):
        QgsApplication.messageLog().logMessage("discard_settings", 'DigitalSketchPlugin')
        self.updated_settings = False
        self.reject()

    def get_attributes(self):
        return self.attributes

    def clear_and_populate_categories(self):
        self.categoryListWidget.clear()
        for pad in self.keypad_manager.data_cpy:
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
            delete_button.setObjectName(pad.category)
            delete_button.setMaximumSize(30, 30)
            delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
            delete_button.clicked.connect(lambda state, db=delete_button: self.delete_keypad_category(db))

            c_box = QCheckBox(pad.category)
            c_box.setObjectName(pad.category)
            select_state = 2 if pad.selected == True else 0
            c_box.setCheckState(select_state)
            c_box.stateChanged.connect(lambda state, cb=c_box: self.checkbox_state_changed(cb, state))

            layout.addWidget(c_box)
            layout.addWidget(colour_picker)
            layout.addWidget(delete_button)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(5)
            widget.setLayout(layout)

            item.setSizeHint(widget.sizeHint())
            self.categoryListWidget.setItemWidget(item, widget)

    def on_category_item_selected(self):
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
                    self.clear_populate_elements_list(c_box.text())

    def clear_populate_elements_list(self, category_name):
        self.elementListWidget.clear()
        category = next((cat for cat in self.keypad_manager.data_cpy if cat.category == category_name), None)
        if category:
            for element in category.items:
                item = QListWidgetItem(self.elementListWidget)
                widget = QWidget()
                layout = QHBoxLayout()
                label = QLabel(element)
                label.setMinimumSize(50, 30)

                space = QSpacerItem(40, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
                obj_name = f'{category.category}:{element}'

                # edit Button (QPushButton)
                edit_button = QPushButton('Edit')
                edit_button.setObjectName(obj_name)
                edit_button.setMinimumSize(40, 30)
                edit_button.setMaximumSize(40, 30)
                edit_button.setStyleSheet("background-color: blue; color: white; border-radius: 5px;")
                edit_button.clicked.connect(lambda state, eb=edit_button: self.edit_keypad_item(eb))

                # Delete Button (QPushButton)
                delete_button = QPushButton('X')
                delete_button.setObjectName(obj_name)
                delete_button.setMinimumSize(30, 30)
                delete_button.setMaximumSize(30, 30)
                delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
                delete_button.clicked.connect(lambda state, db=delete_button: self.delete_keypad_item(db))

                layout.addWidget(label)
                layout.addItem(space)
                layout.addWidget(edit_button)
                layout.addWidget(delete_button)
                layout.setContentsMargins(2, 2, 2, 2)
                layout.setSpacing(5)
                widget.setLayout(layout)

                item.setSizeHint(widget.sizeHint())
                self.elementListWidget.setItemWidget(item, widget)

    def on_element_item_selected(self):
        selected_items = self.elementListWidget.selectedItems()
        if selected_items:
            item = selected_items[0]  # Get the first selected item
            widget = self.elementListWidget.itemWidget(item)  # Get the widget inside

            if widget:
                label = widget.findChild(QLabel)  # Find the checkbox inside the widget
                if label:
                    self.selected_element = label.text()

    def colour_changed(self, colour):
        self.colour = colour.name(QColor.HexArgb)
        QgsApplication.messageLog().logMessage(f'Colour: {self.colour}', 'DigitalSketchPlugin')

    def feature_colour_changed(self, colour):
        self.feature_colour = colour.name(QColor.HexArgb)
        QgsApplication.messageLog().logMessage(f'Colour: {self.colour}', 'DigitalSketchPlugin')

    def set_folder_location(self, folder):
        QgsApplication.messageLog().logMessage(f'Directory path {folder}.', 'DigitalSketchPlugin')
        if folder:
            self.folder_location = folder

    def font_changed(self):
        self.font = self.mFontButton.currentFont()
        QgsApplication.messageLog().logMessage("Font updated", 'DigitalSketchPlugin')

    def change_folder_ctrl_to_readonly(self, folder_location):
        if folder_location is not None and folder_location != '':
            self.folderQgsFileWidget.setReadOnly(True)

    def delete_keypad_category(self, db):
        category = db.objectName()
        if show_delete_confirmation(f'Category: {category}') == QDialog.Accepted:
            self.keypad_manager.remove_category(category)
            self.clear_and_populate_categories()

    def edit_keypad_item(self, eb):
        cat_element = get_category_element(eb.objectName())
        edit_element = EditElement(cat_element[1])
        if edit_element.exec_() == QDialog.Accepted:
            self.keypad_manager.update_item(cat_element[0], cat_element[1], edit_element.get_element_text())
            self.clear_populate_elements_list(self.selected_category)


    def delete_keypad_item(self, db):
        cat_element = get_category_element(db.objectName())
        if show_delete_confirmation(f'Element: {cat_element[1]}') == QDialog.Accepted:
            self.keypad_manager.remove_item(cat_element[0], cat_element[1])
            self.clear_populate_elements_list(self.selected_category)