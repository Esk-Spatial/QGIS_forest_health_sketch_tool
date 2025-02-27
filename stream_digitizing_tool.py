
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsFeature, QgsGeometry
from PyQt5.QtCore import Qt

class StreamDigitizingTool(QgsMapTool):
    def __init__(self, iface, layer, layer_type, is_multipart=False):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.layer = layer
        self.layer_type = layer_type
        self.stream_points = []
        self.multi_part_segments = []
        self.digitizing = False
        self.current_line = []
        self.is_multipart=is_multipart
        self.stylus_down = False
        self.geom_type = QgsWkbTypes.LineGeometry if layer_type == 'line' else QgsWkbTypes.PolygonGeometry
        self.rubber_band = QgsRubberBand(self.canvas(), self.geom_type)
        self.rubber_band.setColor(Qt.red)
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:  # Stylus down
            if not self.digitizing:
                self.start_digitizing(event)
            self.stylus_down = True

    def canvasMoveEvent(self, event):
        if self.digitizing:
            self.add_vertex(event)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # Stylus up
            self.stylus_down = False
            if not self.is_multipart:
                self.finish_digitizing()
            else:
                if len(self.current_line) > 1:  # Ensure it's a valid line
                    self.multi_line_segments.append(self.current_line)

    def start_digitizing(self, event):
        if self.is_multipart:
            self.current_line = [self.toMapCoordinates(event.pos())]  # Start a new line
            self.rubber_band.reset(QgsWkbTypes.LineGeometry)
        else:
            self.stream_points = [self.toMapCoordinates(event.pos())]
            self.rubber_band.reset(QgsWkbTypes.LineGeometry if self.layer_type == 'line' else QgsWkbTypes.PolygonGeometry)
        self.digitizing = True
        self.stylus_down = True

    def add_vertex(self, event):
        point = self.toMapCoordinates(event.pos())
        self.stream_points.append(point)
        self.rubber_band.addPoint(point, True)
        self.rubber_band.show()

    def finish_digitizing(self):
        geom_type = QgsGeometry.fromPolylineXY(
            self.stream_points) if self.layer_type == 'line' else QgsGeometry.fromPolygonXY([self.stream_points])

        if self.is_multipart:
            # Store multi-line parts until Enter is pressed
            self.multi_part_segments.append(geom_type)
            self.stream_points = []
            self.rubber_band.reset(QgsWkbTypes.LineGeometry if self.layer_type == 'line' else QgsWkbTypes.PolygonGeometry)
            return  # Do not save yet

        self.save_feature(geom_type)
        # if not self.stream_points:
        #     return
        # self.digitizing = False
        # geom = QgsGeometry.fromPolylineXY(
        #     self.stream_points) if self.layer_type == 'line' else QgsGeometry.fromPolygonXY([self.stream_points])
        #
        # feature = QgsFeature(self.layer.fields())
        # feature.setGeometry(geom)
        # self.layer.startEditing()
        # self.layer.addFeature(feature)
        # self.layer.commitChanges()
        # self.rubber_band.reset(QgsWkbTypes.LineGeometry if self.layer_type == 'line' else QgsWkbTypes.PolygonGeometry)

    def save_feature(self, geom):
        feature = QgsFeature(self.layer.fields())
        feature.setGeometry(geom)
        self.layer.startEditing()
        self.layer.addFeature(feature)
        self.layer.commitChanges()

        # Reset drawing
        self.rubber_band.reset(QgsWkbTypes.LineGeometry if self.layer_type == 'line' else QgsWkbTypes.PolygonGeometry)
        self.digitizing = False
        self.stream_points = []
        self.multi_part_segments = []