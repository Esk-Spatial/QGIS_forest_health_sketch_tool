
from PyQt5.QtGui import QColor
from qgis.PyQt.QtWidgets import (QDialog, QCheckBox, QWidget, QListWidgetItem, QHBoxLayout,
                                 QLabel, QPushButton, QSpacerItem, QSizePolicy)
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os
from qgis.gui import QgsColorButton
from PyQt5.QtCore import Qt

from add_or_edit_element import AddOrEditElement
from confirmation import ConfirmationDialog
from helper import show_delete_confirmation, get_existing_enabled_layers, get_default_auto_update_interval
from new_category import NewCategory
from select_existing_layer import SelectExistingLayerDialog

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "app_settings.ui"))


def update_colour(pad, colour):
    """Update the colour of the keypad category.

    :param pad: Keypad category
    :type pad: KeypadCategory

    :param colour: New colour
    :type colour: QColor
    """
    pad.colour = colour.name()


def get_category_element(text):
    """Get the category and element from the text.

    :param text: Text to parse
    :type text: str

    :return: Category and element
    """
    return text.split(':')


class AppSettingsDialog(QDialog, FORM_CLASS):
    """App settings dialog."""

    def __init__(self, keypad_manager, attributes, disable_existing=False, parent=None):
        """Constructor.

        :param keypad_manager: Keypad categories and items
        :type keypad_manager: KeypadManager

        :param attributes: Attributes of the existing project
        :type attributes: dict

        :param disable_existing: Whether to disable the use existing layer checkbox
        :type disable_existing: bool

        :param parent: Parent widget
        :type parent: QWidget
        """
        super(AppSettingsDialog, self).__init__(parent)
        self.add_bing_imagery = False
        self.setupUi(self)
        self.keypad_manager = keypad_manager
        self.keypad_manager.load_data()
        self.categoryListWidget.itemSelectionChanged.connect(self.on_category_item_selected)
        self.elementListWidget.itemSelectionChanged.connect(self.on_element_item_selected)
        self.selected_category = ''
        self.selected_element = ''
        self.folder_location = None
        self.colour = self.mColorButton.color().name(QColor.HexArgb)
        self.feature_colour = self.featureColorButton.color().name(QColor.HexArgb)
        self.font = self.mFontButton.currentFont()
        self.height = 26
        self.width = 174
        self.attributes = None
        self.use_existing_layer = False
        self.layers = None
        self.project_changed = False
        self.new_project = False
        self.update_interval = get_default_auto_update_interval()
        self.rotate_recenter_on_done = False
        intervals_list = [5,10,20,30,40,50,60]
        self.autoUpdateComboBox.setCurrentIndex(intervals_list.index(self.update_interval))

        self.toggle_project_name_and_file_read_only_state(True) # setting the project name and folder location to read-only

        # if the attributes are set, then update the app settings attributes and update TextEdit and Picker values.
        if attributes is not None:
            self.projectNameLineEdit.setText(attributes["project_name"])
            if attributes["project_name"] is not None and attributes["project_name"] != '':
                self.projectNameLineEdit.setReadOnly(True)
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
            self.useExistingLayerCheckBox.setChecked(attributes["use_existing"])
            if attributes["use_existing"]:
                self.toggle_project_name_and_file_read_only_state(True)
            self.project_changed = attributes['project_changed'] if attributes['project_changed'] is not None else False
            self.add_bing_imagery = attributes["add_bing_imagery"]
            self.bingImageryCheckBox.setChecked(attributes["add_bing_imagery"])
            self.update_interval = attributes["update_interval"]
            self.autoUpdateComboBox.setCurrentIndex(intervals_list.index(self.update_interval))
            self.rotate_recenter_on_done = attributes["rotate_recenter_on_done"]
            self.rorateAndRecenterCheckBox.setChecked(attributes["rotate_recenter_on_done"])

        if disable_existing:
            self.useExistingLayerCheckBox.setDisabled(True)

        self.updated_settings = False
        self.clear_and_populate_categories()

        # Setup button and widget signals
        self.moveDownPadItemPushButton.clicked.connect(lambda :self.move_category("down"))
        self.moveUpPadItemPushButton.clicked.connect(lambda :self.move_category("up"))
        self.moveDownNeedleItemPushButton.clicked.connect(lambda: self.move_element("down"))
        self.moveUpNeedleItemPushButton.clicked.connect(lambda: self.move_element("up"))

        self.addCategoryPushButton.clicked.connect(lambda: self.add_category())
        self.addElementPushButton.clicked.connect(lambda: self.add_element())

        self.newProjectPushButton.clicked.connect(self.create_new_project)
        self.applyPushButton.clicked.connect(self.apply_settings)
        self.discardPushButton.clicked.connect(self.discard_settings)
        self.mFontButton.changed.connect(self.font_changed)
        self.featureColorButton.colorChanged.connect(self.feature_colour_changed)
        self.mColorButton.colorChanged.connect(self.colour_changed)
        self.folderQgsFileWidget.fileChanged.connect(self.set_folder_location)
        self.useExistingLayerCheckBox.stateChanged.connect(lambda state: self.set_use_existing(state))
        self.bingImageryCheckBox.stateChanged.connect(lambda state: self.set_add_bing_imagery(state))
        self.rorateAndRecenterCheckBox.stateChanged.connect(self.set_rotate_and_recenter)
        self.autoUpdateComboBox.currentIndexChanged.connect(self.gps_auto_update_interval_updated)


    def move_category(self, direction):
        """Move the selected keypad category up or down.

        :param direction: Direction to move the category, either "up" or "down"
        :type direction: str
        """
        self.keypad_manager.move_category(self.selected_category,direction)
        self.clear_and_populate_categories()


    def move_element(self, direction):
        """Move the selected keypad element up or down.

        :param direction: Direction to move the element, either "up" or "down"
        :type direction: str
        """
        self.keypad_manager.move_item(self.selected_category, self.selected_element, direction)
        self.clear_populate_elements_list(self.selected_category)


    def checkbox_state_changed(self, checkbox, state):
        """Handle the state change of a keypad category checkbox.

        :param checkbox: The checkbox widget
        :type checkbox: QWidget

        :param state: The new state of the checkbox
        :type state: int
        """
        self.keypad_manager.set_category_selection(checkbox.objectName(), state)


    def add_category(self):
        """Add a new keypad category."""

        add_dialog = NewCategory()
        if add_dialog.exec_() == QDialog.Accepted:
            data = add_dialog.get_add_data()
            if data:
                self.keypad_manager.add_category(data)
                self.clear_and_populate_categories()


    def add_element(self):
        """Add a new keypad element to the selected category."""

        if self.selected_category == '':
            return

        add_element = AddOrEditElement()
        if add_element.exec_() == QDialog.Accepted:
            data = add_element.get_item()
            if data.item != "":
                self.keypad_manager.add_item(self.selected_category, data)
                self.clear_populate_elements_list(self.selected_category)


    def gps_auto_update_interval_updated(self, index):
        """Update the interval value when the combobox value is changed.

        :param index: Index of the selected item in the combobox
        :type index: int
        """
        self.update_interval = int(self.autoUpdateComboBox.itemText(index))


    def apply_settings(self):
        """Apply the app settings to the project."""

        self.updated_settings = True
        self.attributes = {
            "project_name" : self.projectNameLineEdit.text().strip(),
            "folder_path" : self.folder_location,
            "use_existing" : self.use_existing_layer,
            "layers" : self.layers,
            "new_project" : self.new_project,
            "feature_colour" : self.feature_colour,
            "surveyor" : self.surveyourLineEdit.text().strip(),
            "type_txt" : self.typeLineEdit.text().strip(),
            "font" : self.font,
            "colour" : self.colour,
            "height" : int(self.heightLineEdit.text().strip()),
            "width" : int(self.widthLineEdit.text().strip()),
            "project_changed" : self.project_changed,
            "add_bing_imagery" : self.add_bing_imagery,
            "update_interval": self.update_interval,
            "rotate_recenter_on_done": self.rotate_recenter_on_done
        }
        self.keypad_manager.update_dataset()
        self.accept()


    def discard_settings(self):
        """Discard the app settings and close the dialog."""
        self.updated_settings = False
        self.reject()


    def get_attributes(self):
        """Gets the settings attributes.

        "return: Attributes of the existing project
        """
        return self.attributes


    def clear_and_populate_categories(self):
        """Clear and populate the keypad categories list widget.

        When initializing the view or when a category is added, updated, or removed, then this function will be called.
        Create signal handlers for the checkbox, delete button, and colour picker widgets.
        Added a label such that for selecting a category, clicking on the checkbox is required
        """
        self.categoryListWidget.clear()
        for pad in self.keypad_manager.data:
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
            delete_button.setMinimumSize(30, 30)
            delete_button.setMaximumSize(30, 30)
            delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
            delete_button.clicked.connect(lambda state, db=delete_button: self.delete_keypad_category(db))

            label = QLabel(pad.category)

            c_box = QCheckBox("")
            c_box.setObjectName(pad.category)
            select_state = 2 if pad.selected == True else 0
            c_box.setCheckState(select_state)
            c_box.stateChanged.connect(lambda state, cb=c_box: self.checkbox_state_changed(cb, state))

            layout.addWidget(c_box)
            layout.addWidget(label)
            layout.addItem(QSpacerItem(30, 30, QSizePolicy.Expanding, QSizePolicy.Minimum))
            layout.addWidget(colour_picker)
            layout.addWidget(delete_button)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(5)
            widget.setLayout(layout)

            item.setSizeHint(widget.sizeHint())
            self.categoryListWidget.setItemWidget(item, widget)


    def on_category_item_selected(self):
        """Handle the selection of a keypad category item.
        Populate the keypad elements list widget with the selected category's elements.
        """
        selected_items = self.categoryListWidget.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]  # Get the first selected item
        widget = self.categoryListWidget.itemWidget(item)  # Get the widget inside

        if not widget:
            return

        c_box = widget.findChild(QCheckBox)  # Find the checkbox inside the widget
        if c_box:
            self.selected_category = c_box.objectName()
            self.padItemsGroupBox.setTitle(f'Keypad: {self.selected_category}')
            self.clear_populate_elements_list(self.selected_category)


    def clear_populate_elements_list(self, category_name):
        """Clear and populate the keypad elements list widget for the selected category.
        Create signal handlers for delete and edit buttons.

        :param category_name: Name of the category
        :type category_name: str
        """
        self.elementListWidget.clear()
        category = next((cat for cat in self.keypad_manager.data if cat.category == category_name), None)
        if not category:
            return

        for element in category.items:
            item = QListWidgetItem(self.elementListWidget)
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(element.item)
            label.setMinimumSize(50, 30)

            space = QSpacerItem(40, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
            obj_name = f'{category.category}:{element.item}'

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
        """Handle the selection of a keypad element item."""
        selected_items = self.elementListWidget.selectedItems()
        if selected_items:
            item = selected_items[0]  # Get the first selected item
            widget = self.elementListWidget.itemWidget(item)  # Get the widget inside

            if widget:
                label = widget.findChild(QLabel)  # Find the checkbox inside the widget
                if label:
                    self.selected_element = label.text()


    def colour_changed(self, colour):
        """Handles the colour change event.

        :param colour: The new colour
        :type colour: QColor
        """
        self.colour = colour.name(QColor.HexArgb)


    def feature_colour_changed(self, colour):
        """Handles the feature colour change event.

        :param colour: The new colour
        :type colour: QColor
        """
        self.feature_colour = colour.name(QColor.HexArgb)


    def set_folder_location(self, folder):
        """Set the folder location."""
        if folder:
            self.folder_location = folder


    def set_use_existing(self, state):
        self.use_existing_layer = state == Qt.Checked
        if self.use_existing_layer:
            layer_selection = SelectExistingLayerDialog(get_existing_enabled_layers())
            if layer_selection.exec_() == QDialog.Accepted:
                self.layers = layer_selection.get_layer_selection()
                self.toggle_project_name_and_file_read_only_state(True)
        else:
            self.toggle_project_name_and_file_read_only_state(False)


    def set_add_bing_imagery(self, state):
        self.add_bing_imagery = state == Qt.Checked


    def set_rotate_and_recenter(self, state):
        self.rotate_recenter_on_done = state == Qt.Checked


    def font_changed(self):
        self.font = self.mFontButton.currentFont()


    def change_folder_ctrl_to_readonly(self, folder_location):
        if folder_location is not None and folder_location != '':
            self.folderQgsFileWidget.setReadOnly(True)
            self.useExistingLayerCheckBox.setDisabled(True) # if the folder is set, then use existing checkbox is disabled


    def toggle_project_name_and_file_read_only_state(self, state):
        self.folderQgsFileWidget.setReadOnly(state)
        self.projectNameLineEdit.setReadOnly(state)


    def delete_keypad_category(self, db):
        """Function will be called when keypad category delete button is clicked.
        Shows a confirmation dialog before deleting the category

        :param db: The button object
        :type db: QPushButton
        """
        category = db.objectName()
        if show_delete_confirmation(f'Category: {category}') == QDialog.Accepted:
            self.elementListWidget.clear()
            self.keypad_manager.remove_category(category)
            self.clear_and_populate_categories()


    def edit_keypad_item(self, eb):
        """Function will be called when keypad item edit button is clicked.
        Opens a dialog to edit the element name.

        :param eb: The button object
        :type eb: QPushButton
        """
        cat_element = get_category_element(eb.objectName())
        edit_element = AddOrEditElement(cat_element[1])
        if edit_element.exec_() == QDialog.Accepted:
            self.keypad_manager.update_item(cat_element[0], cat_element[1], edit_element.get_item())
            self.clear_populate_elements_list(self.selected_category)


    def delete_keypad_item(self, db):
        """Function will be called when keypad item delete button is clicked.
        Shows a confirmation dialog before deleting the element.

        :param db: The button object
        :type db: QPushButton
        """
        cat_element = get_category_element(db.objectName())
        if show_delete_confirmation(f'Element: {cat_element[1]}') == QDialog.Accepted:
            self.keypad_manager.remove_item(cat_element[0], cat_element[1])
            self.clear_populate_elements_list(cat_element[0])


    def create_new_project(self):
        """Called when Create new project button is clicked.

        This will show the confirmation dialog and clear the selection if confirmed.
        """
        confirmation = ConfirmationDialog()
        if confirmation.exec_() == QDialog.Accepted:
            self.new_project = True
            self.clear_selection()
            self.useExistingLayerCheckBox.setDisabled(True)


    def clear_selection(self):
        """Clear the fields for project name, location and enable those fields to be edited.
        Clear exisiting layer and use bing imager check boxes.
        """
        self.projectNameLineEdit.setText('')
        self.projectNameLineEdit.setReadOnly(False)
        self.folderQgsFileWidget.setFilePath('')
        self.folderQgsFileWidget.setReadOnly(False)
        self.useExistingLayerCheckBox.setChecked(False)
        self.bingImageryCheckBox.setChecked(False)