
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "help.ui"))

class HelpDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.setupUi(self)
