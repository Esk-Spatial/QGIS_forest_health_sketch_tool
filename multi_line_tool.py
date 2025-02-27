from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsFeature, QgsGeometry
from PyQt5.QtCore import Qt

class MultiLineDigitizingTool(QgsMapTool):
    def __init__(self, iface, layer):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.layer = layer
        self.digitizing = False
        self.stylus_down = False
        self.current_line = []
        self.multi_line_segments = []  # Stores all individual lines
        self.rubber_band = QgsRubberBand(self.canvas(), QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(Qt.red)
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        """Start a new line segment on stylus down"""
        if event.button() == Qt.LeftButton:
            self.stylus_down = True
            self.current_line = [self.toMapCoordinates(event.pos())]  # Start a new line
            # self.rubber_band.reset(QgsWkbTypes.LineGeometry)

    def canvasMoveEvent(self, event):
        """Continue adding points to the current line"""
        if self.stylus_down:
            point = self.toMapCoordinates(event.pos())
            self.current_line.append(point)
            self.rubber_band.addPoint(point, True)
            self.rubber_band.show()

    def canvasReleaseEvent(self, event):
        """Store the completed line segment on stylus up"""
        if event.button() == Qt.LeftButton:
            self.stylus_down = False
            if len(self.current_line) > 1:  # Ensure it's a valid line
                self.multi_line_segments.append(self.current_line)  # Store as a new segment
                self.update_rubber_band()

    def keyPressEvent(self, event):
        """Save MultiLineString when Enter is pressed"""
        if event.key() == Qt.Key_Return:
            self.save_multiline_feature()

    def update_rubber_band(self):
        """Updates the rubber band to display all drawn lines"""
        self.rubber_band.reset(QgsWkbTypes.LineGeometry)
        for line in self.multi_line_segments + ([self.current_line] if self.current_line else []):
            for pt in line:
                self.rubber_band.addPoint(pt, False)
        self.rubber_band.show()

    def save_multiline_feature(self):
        """Saves the drawn MultiLineString to the layer"""
        multiline_geom = QgsGeometry.fromMultiPolylineXY(self.multi_line_segments)
        feature = QgsFeature(self.layer.fields())
        feature.setGeometry(multiline_geom)

        self.layer.startEditing()
        self.layer.addFeature(feature)
        self.layer.commitChanges()

        # Reset state
        self.multi_line_segments = []
        self.rubber_band.reset(QgsWkbTypes.LineGeometry)

