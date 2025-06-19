
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from helper import get_existing_enabled_layers

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "select_existing_layer.ui"))


def add_items_to_combo_box(items, combo_box):
    """Add items to the combo box.
    If there is more than one item, then add a select item to the top of the combo box.

    :param items: Items to add
    :type items: a list

    :param combo_box: Combo box to add items to
    :type combo_box: QComboBox
    """
    if len(items) > 1:
        combo_box.addItem('Select')
    for item in items:
        combo_box.addItem(item['name'])

def get_selection_layer(items, combo_box):
    """Get the selected layer from the combo box.
    If there is only one item, then return the layer.
    Else, return the layer at the index - 1 of the selected item to account for the select item at the top of the combo box.

    :param items: Items list
    :type items: a list

    :param combo_box: Combo box
    :type combo_box: QComboBox

    :return: Selected layer name
    """
    if len(items) == 0:
        return None
    if len(items) == 1:
        return items[0]['layer']
    else:
        return items[combo_box.currentIndex()-1]['layer']


class SelectExistingLayerDialog(QDialog, FORM_CLASS):
    def __init__(self, layer_groups, parent=None):
        """Constructor.

        :param layer_groups: Layer groups
        :type layer_groups: dict

        :param parent: Parent widget
        :type parent: QWidget, optional
        """
        super(SelectExistingLayerDialog, self).__init__(parent)
        # set up the UI components and button clicked signals.
        self.setupUi(self)
        self.layer_groups = layer_groups

        add_items_to_combo_box(self.layer_groups['points'], self.pointsComboBox)
        add_items_to_combo_box(self.layer_groups['polygons'], self.polygonsComboBox)
        add_items_to_combo_box(self.layer_groups['lines'], self.linesComboBox)

        self.confirmPushButton.clicked.connect(self.confirm_changes)
        self.rejectPushButton.clicked.connect(self.discard_changes)

    def confirm_changes(self):
        """This function will be fired when and if the user clicks on the Confirm button."""
        self.accept()

    def discard_changes(self):
        """This function will be fired when and if the user clicks on the Reject button."""
        self.reject()

    def get_layer_selection(self):
        """Get the selected layers from the combo boxes.

        :return: Selected layers dictionary
        """
        layers = dict()
        layers['points'] = get_selection_layer(self.layer_groups['points'], self.pointsComboBox)
        layers['polygons'] = get_selection_layer(self.layer_groups['polygons'], self.polygonsComboBox)
        layers['lines'] = get_selection_layer(self.layer_groups['lines'], self.linesComboBox)

        return layers