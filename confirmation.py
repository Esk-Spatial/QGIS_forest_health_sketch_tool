from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "confirmation.ui"))

class ConfirmationDialog(QDialog, FORM_CLASS):
    """Confirmation Dialog"""
    def __init__(self, parent=None):
        super(ConfirmationDialog, self).__init__(parent)
        self.setupUi(self)

        self.confirmPushButton.clicked.connect(self.confirm_new_project)
        self.rejectPushButton.clicked.connect(self.reject_new_project)

    def confirm_new_project(self):
        self.accept()

    def reject_new_project(self):
        self.reject()