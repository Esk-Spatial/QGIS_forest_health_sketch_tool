
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from keypad_manager import Keypad

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "new_category_element.ui"))

class NewCategoryElement(QDialog, FORM_CLASS):
    def __init__(self, mode, parent=None):
        super(NewCategoryElement, self).__init__(parent)
        self.result_data = None
        self.setupUi(self)
        self.mode = mode
        if mode == 'category':
            QgsApplication.messageLog().logMessage("Mode: category", 'DigitalSketchPlugin')
            self.elementGroupBox.setVisible(False)
            self.categoryGroupBox.setVisible(True)

        else:
            QgsApplication.messageLog().logMessage("Mode: element", 'DigitalSketchPlugin')
            self.elementGroupBox.setVisible(True)
            self.categoryGroupBox.setVisible(False)

        self.applyPushButton.clicked.connect(self.add_new_category_element)
        self.discardPushButton.clicked.connect(self.discard_new_category_element)


    def add_new_category_element(self):
        QgsApplication.messageLog().logMessage("add_new_category_element", 'DigitalSketchPlugin')
        if self.mode == 'category':
            category = self.categoryLineEdit.text()
            colour = self.mColorButton.color().name()
            element_str = self.elementsTextEdit.toPlainText()

            if ',' in element_str:
                elements = [e.strip() for e in element_str.split(',')]

            else:
                elements = [element_str]

            category = Keypad(category, False, colour, elements)
            QgsApplication.messageLog().logMessage(f"category: {category}", 'DigitalSketchPlugin')
            self.result_data = category
            self.accept()

        else:
            element = self.elementLineEdit.text()
            QgsApplication.messageLog().logMessage(f"element: {element}", 'DigitalSketchPlugin')
            self.result_data = element
            self.accept()

    def discard_new_category_element(self):
        QgsApplication.messageLog().logMessage("discard_new_category_element", 'DigitalSketchPlugin')
        self.reject()

    def get_add_data(self):
        return getattr(self, "result_data", None)
