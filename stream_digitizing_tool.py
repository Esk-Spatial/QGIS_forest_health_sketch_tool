
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsFeature, QgsGeometry, QgsApplication, QgsProject, Qgis
from PyQt5.QtCore import Qt
from qgis.PyQt.QtGui import QColor

from helper import update_feature_attributes, reproject_to_destination_crs


class StreamDigitizingTool(QgsMapTool):
    def __init__(self, iface, layer, layer_type):
        """Constructor

        :param iface: QGIS interface
        :type iface: QgsInterface

        :param layer: QGIS layer, Point or Polygon
        :type layer: QgsVectorLayer

        :param layer_type: Type of layer, points/polygons
        :type layer_type: str
        """
        super().__init__(iface.mapCanvas())
        self.number_of_items_to_update = 1
        self.iface = iface
        self.layer = layer
        self.layer_type = layer_type
        self.stream_points = []
        self.pending_features = []
        self.digitizing = False
        self.rubber_band = QgsRubberBand(self.iface.mapCanvas(),
                                         QgsWkbTypes.PointGeometry if layer_type == 'points' else QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(Qt.red)
        if layer_type == 'polygons':
            self.rubber_band.setFillColor(QColor(255, 0, 0, 25))
        self.rubber_band.setWidth(2)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.layer_type == 'points':
                self.add_point(event)
            else:
                self.start_digitizing(event)

    def canvasMoveEvent(self, event):
        if self.digitizing:
            self.add_vertex(event)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.layer_type != 'points':
            self.finish_digitizing()

    def start_digitizing(self, event):
        self.stream_points = [self.toMapCoordinates(event.pos())]
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
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
        # self.temp_rubber_band.setToGeometry(geom, None)

    def populate_feature_for_polygon(self):
        geom = QgsGeometry.fromPolygonXY([self.stream_points])

        canvas_crs = QgsProject.instance().crs()
        layer_crs = self.layer.crs()

        if canvas_crs != layer_crs:
            geom = reproject_to_destination_crs(geom, canvas_crs, layer_crs)

        feature = QgsFeature(self.layer.fields())
        feature.setGeometry(geom)
        self.pending_features.append(feature)

    def add_point(self, event):
        point = self.toMapCoordinates(event.pos())
        self.rubber_band.addPoint(point, True)
        self.rubber_band.show()

        canvas_crs = QgsProject.instance().crs()
        layer_crs = self.layer.crs()
        geom = QgsGeometry.fromPointXY(point)
        if canvas_crs != layer_crs:
            geom = reproject_to_destination_crs(geom, canvas_crs, layer_crs)

        feature = QgsFeature(self.layer.fields())
        feature.setGeometry(geom)
        self.pending_features.append(feature)

    def features_to_save(self):
        """Checks if there are any features to save.

        :return: True if there are features to save, False otherwise.
        """
        if self.layer_type == 'points':
            return len(self.pending_features) > 0
        else:
            return len(self.stream_points) > 0

    def save_feature(self, attributes):
        if self.layer_type != 'points':
            self.populate_feature_for_polygon()
        if not self.pending_features:
            return
        if not self.layer.isEditable():
            self.layer.startEditing()

        self.number_of_items_to_update = len(self.pending_features)
        for feature in self.pending_features:
            if feature.geometry() is None:
                self.iface.messageBar().pushMessage("Warning", "Geometry is None.", level=Qgis.Warning, duration=5)
                continue
            self.layer.addFeature(update_feature_attributes(feature, self.layer_type, attributes))

        self.pending_features = []
        self.stream_points = []
        self.layer.commitChanges()
        self.layer.startEditing()
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry if self.layer_type == 'polygons' else QgsWkbTypes.PointGeometry)

    def remove_feature(self):
        QgsApplication.messageLog().logMessage(f'layer_type: {self.layer_type}', 'DigitalSketchPlugin')
        if self.layer_type == 'points':
            if len(self.pending_features) > 0:
                self.pending_features.pop()
                self.rubber_band.removeLastPoint()
                self.rubber_band.show()
        else:
            self.stream_points = []
            self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)