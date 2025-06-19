from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import (QgsWkbTypes, QgsPointXY, QgsFeature, QgsGeometry, QgsMultiLineString, QgsLineString, QgsProject,
                       QgsApplication)
from PyQt5.QtCore import Qt

from helper import update_feature_attributes, reproject_to_destination_crs


class MultiLineDigitizingTool(QgsMapTool):
    def __init__(self, iface, layer):
        """Constructor

        :param iface: QGIS interface
        :type iface: QgsInterface

        :param layer: QGIS multi line layer
        :type layer: QgsVectorLayer
        """
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.number_of_items_to_update = 1
        self.layer = layer
        self.stylus_down = False
        self.current_line = []
        self.multi_line_segments = []  # Stores all individual lines
        self.rubber_band = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.LineGeometry) # QgsWkbTypes.LineGeometry
        self.rubber_band.setColor(Qt.red)
        self.rubber_band.setWidth(4)

    def canvasPressEvent(self, event):
        """Start a new line segment on stylus down

        :param event: The mouse event object containing details about the button press interaction on the map canvas
        :type event: QgsMapMouseEvent
        """
        if event.button() == Qt.LeftButton:
            self.stylus_down = True
            self.current_line = [self.toMapCoordinates(event.pos())]  # Start a new line

    def canvasMoveEvent(self, event):
        """Continue adding points to the current line

        :param event: The mouse event object containing details about the movement interaction on the map canvas
        :type event: QgsMapMouseEvent
        """
        if self.stylus_down:
            point = self.toMapCoordinates(event.pos())
            self.current_line.append(point)
            self.update_rubber_band()

    def canvasReleaseEvent(self, event):
        """Store the completed line segment on stylus up

        :param event: The mouse event object containing details about the mouse button release interaction on the map canvas
        :type event: QgsMapMouseEvent
        """
        if event.button() == Qt.LeftButton:
            self.stylus_down = False
            if len(self.current_line) > 1:  # Ensure it's a valid line
                self.multi_line_segments.append(self.current_line)  # Store as a new segment
                self.update_rubber_band()

    def update_rubber_band(self):
        """Converts the lines to multi lines Updates the rubber band to display all drawn lines"""
        multi_line = self.get_multiline_string()

        if self.current_line:
            multi_line.addGeometry(QgsLineString(self.current_line))

        self.rubber_band.setToGeometry(QgsGeometry(multi_line), None)

    def features_to_save(self):
        """Checks if there are any lines to save

        :return: True if there are lines to save, False otherwise
        """
        return len(self.multi_line_segments) > 0


    def save_feature(self, attributes):
        """Saves the drawn MultiLineString to the layer.
        If the map CRS is different to the layer, then reproject the geometry.
        If the layer is not editable, make the layer editable if there is a valid feature to save, then commit the changes.
        """
        if not self.multi_line_segments:
            return

        canvas_crs = QgsProject.instance().crs()
        layer_crs = self.layer.crs()

        multi_line = self.get_multiline_string()

        if canvas_crs != layer_crs:
            multi_line = reproject_to_destination_crs(multi_line, canvas_crs, layer_crs)

        feature = QgsFeature(self.layer.fields())
        feature.setGeometry(QgsGeometry(multi_line))

        if not self.layer.isEditable():
            self.layer.startEditing()

        if self.layer.addFeature(update_feature_attributes(feature, '', attributes)):
            self.layer.commitChanges()

        else:
            self.layer.rollBack()

        # Reset state
        self.multi_line_segments = []
        self.layer.startEditing()
        self.rubber_band.reset(QgsWkbTypes.LineGeometry)

    def get_multiline_string(self):
        """Converts the list of line segments to a QgsMultiLineString

        :return: QgsMultiLineString
        """
        multi_line = QgsMultiLineString()
        for line in self.multi_line_segments:
            multi_line.addGeometry(QgsLineString(line))

        return multi_line

    def remove_feature(self):
        """Remove the last unsaved line segment from the list and reset the rubber band."""
        self.multi_line_segments = []
        self.rubber_band.reset(QgsWkbTypes.LineGeometry)