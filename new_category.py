
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from keypad_manager import Keypad, KeypadItem

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "new_category.ui"))

class NewCategory(QDialog, FORM_CLASS):
    """New category dialog."""
    def __init__(self, parent=None):
        """Constructor.

        :param parent: Parent widget for the new category dialog.
        :type parent: QWidget, optional
        """
        super(NewCategory, self).__init__(parent)

        # set up the placeholders and button clicked signals.
        self.result_data = None
        self.setupUi(self)
        self.applyPushButton.clicked.connect(self.add_new_category)
        self.discardPushButton.clicked.connect(self.discard_new_category)


    def add_new_category(self):
        """This function is triggered when the apply, button is clicked.
        Add a new category to the Keypad."""
        category = self.categoryLineEdit.text()
        colour = self.mColorButton.color().name()
        element_str = self.elementsTextEdit.toPlainText()

        # if there are multiple items defined, then split the elements on ','
        if ',' in element_str:
            elements = [{"item_id": 0, "item": e.strip()} for e in element_str.split(',')]

        else:
            elements = [{"item_id": 0, "item": element_str}]

        # creating the Keypad Category object.
        category = Keypad(0, category, False, colour, elements)
        self.result_data = category
        self.accept()


    def discard_new_category(self):
        """Discard the new category creation."""
        self.reject()

    def get_add_data(self):
        """Get the new category data."""
        return getattr(self, "result_data", None)
