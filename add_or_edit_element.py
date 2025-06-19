
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from keypad_manager import KeypadItem

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "add_or_edit_element.ui"))

class AddOrEditElement(QDialog, FORM_CLASS):
    def __init__(self, item=None, parent=None):
        """Constructor.

        :param item: KeypadItem object
        :type item: KeypadItem, optional

        :param parent: Parent widget
        :type parent: QWidget, optional
        """
        super(AddOrEditElement, self).__init__(parent)
        # Set up UI elements and set up button clicked signals
        self.item = item if item is not None else KeypadItem(0, "")
        self.setupUi(self)

        self.elementLineEdit.setText(self.item.item)
        self.applyPushButton.clicked.connect(self.apply_changes)
        self.discardPushButton.clicked.connect(self.discard_changes)

    def apply_changes(self):
        """Apply the changes to the KeypadItem object. This function is triggered when the apply, button is clicked."""
        self.item.item = self.elementLineEdit.text()
        self.accept()

    def discard_changes(self):
        """Discard the changes to the KeypadItem object. This function is triggered when the discard, button is clicked."""
        self.reject()

    def get_item(self):
        """Get the KeypadItem object.

        :return: KeypadItem object
        """
        return self.item