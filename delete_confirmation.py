
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
import os

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "delete_confirmation.ui"))

class DeleteConfirmationDialog(QDialog, FORM_CLASS):
    def __init__(self, text, parent=None):
        """Constructor for the DeleteConfirmationDialog.

        :param text: The text to display in the confirmation dialog.
        :type text: str
        :param parent: The parent widget for the confirmation dialog.
        :type parent: QWidget, optional
        """
        super(DeleteConfirmationDialog, self).__init__(parent)
        self.setupUi(self)

        self.txtLabel.setText(f'Are you sure you want to delete the {text}')
        self.confirmPushButton.clicked.connect(self.confirm_delete)
        self.rejectPushButton.clicked.connect(self.reject_delete)

    def confirm_delete(self):
        self.accept()

    def reject_delete(self):
        self.reject()