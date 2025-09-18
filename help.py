
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "help.ui"))

class HelpDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.setupUi(self)
        plugin_dir = os.path.dirname(__file__)  # directory of the current .py file
        help_path = os.path.join(plugin_dir, "help", "help.html")

        self.helpTextBrowser.setSource(QUrl.fromLocalFile(help_path))
