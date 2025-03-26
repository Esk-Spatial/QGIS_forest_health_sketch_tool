
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "edit_element.ui"))

class EditElement(QDialog, FORM_CLASS):
    def __init__(self, element_txt, parent=None):
        super(EditElement, self).__init__(parent)
        self.element_txt = element_txt
        self.setupUi(self)

        self.elementLineEdit.setText(self.element_txt)
        self.applyPushButton.clicked.connect(self.apply_changes)
        self.discardPushButton.clicked.connect(self.discard_changes)

    def apply_changes(self):
        QgsApplication.messageLog().logMessage("apply_changes", 'DigitalSketchPlugin')
        self.element_txt = self.elementLineEdit.text()
        self.accept()

    def discard_changes(self):
        QgsApplication.messageLog().logMessage("discard_changes", 'DigitalSketchPlugin')
        self.reject()

    def get_element_text(self):
        return self.element_txt