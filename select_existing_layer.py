
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from helper import get_existing_enabled_layers

# Load the UI file dynamically
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "select_existing_layer.ui"))


def add_items_to_combo_box(items, combo_box):
    if len(items) > 1:
        combo_box.addItem('Select')
    for item in items:
        combo_box.addItem(item['name'])

def get_selection_layer(items, combo_box):
    QgsApplication.messageLog().logMessage(f"{combo_box.currentIndex()}", 'DigitalSketchPlugin')
    if len(items) == 0:
        return None
    if len(items) == 1:
        return items[0]['layer']
    else:
        return items[combo_box.currentIndex()-1]['layer']


class SelectExistingLayerDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SelectExistingLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.layer_groups = {
            'points': [],
            'polygons': [],
            'lines': []
        }

        existing_layers = get_existing_enabled_layers()

        for l_id, layer in existing_layers.items():
            entry = {'name': layer.name(), 'layer': layer}
            if 'sketch-points' in layer.name():
                self.layer_groups['points'].append(entry)
            elif 'sketch-polygons' in layer.name():
                self.layer_groups['polygons'].append(entry)
            elif 'sketch-lines' in layer.name():
                self.layer_groups['lines'].append(entry)

        add_items_to_combo_box(self.layer_groups['points'], self.pointsComboBox)
        add_items_to_combo_box(self.layer_groups['polygons'], self.polygonsComboBox)
        add_items_to_combo_box(self.layer_groups['lines'], self.linesComboBox)

        self.confirmPushButton.clicked.connect(self.confirm_changes)
        self.rejectPushButton.clicked.connect(self.discard_changes)

    def confirm_changes(self):
        QgsApplication.messageLog().logMessage("confirm_changes", 'DigitalSketchPlugin')
        self.accept()

    def discard_changes(self):
        QgsApplication.messageLog().logMessage("discard_changes", 'DigitalSketchPlugin')
        self.reject()

    def get_layer_selection(self):
        layers = dict()
        layers['points'] = get_selection_layer(self.layer_groups['points'], self.pointsComboBox)
        layers['polygons'] = get_selection_layer(self.layer_groups['polygons'], self.polygonsComboBox)
        layers['lines'] = get_selection_layer(self.layer_groups['lines'], self.linesComboBox)

        return layers