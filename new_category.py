
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from keypad_manager import Keypad, KeypadItem

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "new_category.ui"))

class NewCategory(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(NewCategory, self).__init__(parent)
        self.result_data = None
        self.setupUi(self)
        self.applyPushButton.clicked.connect(self.add_new_category)
        self.discardPushButton.clicked.connect(self.discard_new_category)


    def add_new_category(self):
        QgsApplication.messageLog().logMessage("add_new_category_element", 'DigitalSketchPlugin')
        category = self.categoryLineEdit.text()
        colour = self.mColorButton.color().name()
        element_str = self.elementsTextEdit.toPlainText()

        if ',' in element_str:
            elements = [{"item_id": 0, "item": e.strip()} for e in element_str.split(',')]

        else:
            elements = [{"item_id": 0, "item": element_str}]

        category = Keypad(0, category, False, colour, elements)
        QgsApplication.messageLog().logMessage(f"category: {category}", 'DigitalSketchPlugin')
        self.result_data = category
        self.accept()


    def discard_new_category(self):
        QgsApplication.messageLog().logMessage("discard_new_category", 'DigitalSketchPlugin')
        self.reject()

    def get_add_data(self):
        return getattr(self, "result_data", None)
