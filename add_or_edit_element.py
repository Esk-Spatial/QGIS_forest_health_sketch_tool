
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from keypad_manager import KeypadItem

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "add_or_edit_element.ui"))

class AddOrEditElement(QDialog, FORM_CLASS):
    def __init__(self, item=None, parent=None):
        super(AddOrEditElement, self).__init__(parent)
        self.item = item if item is not None else KeypadItem(0, "")
        self.setupUi(self)

        self.elementLineEdit.setText(self.item.item)
        self.applyPushButton.clicked.connect(self.apply_changes)
        self.discardPushButton.clicked.connect(self.discard_changes)

    def apply_changes(self):
        QgsApplication.messageLog().logMessage("apply_changes", 'DigitalSketchPlugin')
        self.item.item = self.elementLineEdit.text()
        self.accept()

    def discard_changes(self):
        QgsApplication.messageLog().logMessage("discard_changes", 'DigitalSketchPlugin')
        self.reject()

    def get_item(self):
        # return {"item_id": self.item.item_id, "item": self.item.item}
        return self.item