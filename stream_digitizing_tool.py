
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsFeature, QgsGeometry, QgsApplication
from PyQt5.QtCore import Qt

class StreamDigitizingTool(QgsMapTool):
    def __init__(self, iface, layer, layer_type):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.layer = layer
        self.layer_type = layer_type
        self.stream_points = []
        self.pending_features = []
        self.digitizing = False
        self.rubber_band = QgsRubberBand(self.canvas(),
                                         QgsWkbTypes.LineGeometry if layer_type == 'line' else QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(Qt.red)
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:  # Stylus down
            self.start_digitizing(event)

    def canvasMoveEvent(self, event):
        if self.digitizing:
            self.add_vertex(event)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # Stylus up
            self.finish_digitizing()

    def start_digitizing(self, event):
        self.stream_points = [self.toMapCoordinates(event.pos())]
        self.rubber_band.reset(QgsWkbTypes.LineGeometry if self.layer_type == 'line' else QgsWkbTypes.PolygonGeometry)
        self.digitizing = True

    def add_vertex(self, event):
        point = self.toMapCoordinates(event.pos())
        self.stream_points.append(point)
        self.rubber_band.addPoint(point, True)
        self.rubber_band.show()

    def finish_digitizing(self):
        if not self.stream_points:
            return
        self.digitizing = False
        geom = QgsGeometry.fromPolylineXY(
            self.stream_points) if self.layer_type == 'line' else QgsGeometry.fromPolygonXY([self.stream_points])

        feature = QgsFeature(self.layer.fields())
        feature.setGeometry(geom)
        self.pending_features.append(feature)
        # self.temp_rubber_band.setToGeometry(geom, None)

    def save_feature(self):
        if not self.pending_features:
            return

        self.layer.startEditing()
        for feature in self.pending_features:
            self.layer.addFeature(feature)

        self.layer.commitChanges()
        self.rubber_band.reset()
        self.pending_features = []