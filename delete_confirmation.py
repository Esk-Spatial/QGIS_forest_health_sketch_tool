
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os
from new_category_element import NewCategoryElement

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "delete_confirmation.ui"))

class DeleteConfirmationDialog(QDialog, FORM_CLASS):
    def __init__(self, text, parent=None):
        super(DeleteConfirmationDialog, self).__init__(parent)
        self.setupUi(self)

        self.txtLabel.setText(f'Are you sure you want to delete: {text}?')
        self.confirmPushButton.clicked.connect(self.confirm_delete)
        self.rejectPushButton.clicked.connect(self.reject_delete)

    def confirm_delete(self):
        self.accept()

    def reject_delete(self):
        self.reject()