from qgis.core import QgsProject, QgsApplication, QgsMarkerSymbol, Qgis
from qgis.gui import QgsMapTool, QgsMapMouseEvent, QgsMapToolIdentify, QgsHighlight, QgsVertexMarker
from PyQt5.QtCore import Qt
from qgis.PyQt.QtGui import QColor

class FeatureIdentifyTool(QgsMapTool):
    def __init__(self, iface, sketch_tool):
        """Constructor.

        :param iface: QGIS interface object.
        :type iface: QgsInterface

        :param sketch_tool: DigitalSketchMappingTool plugin.
        :type sketch_tool: DigitalSketchMappingTool
        """
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.setCursor(Qt.ArrowCursor)  # Keep normal cursor
        self.tool = sketch_tool

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        """
        Handles the release event triggered by the map canvas mouse interaction. It identifies all the features
        beneath the click position and determines if they belong to the sketch layer.
        If a feature from the sketch layer is found, it highlights the feature.

        Parameters:
            event (QgsMapMouseEvent): The mouse event object containing details about the interaction
            on the map canvas.
        """
        identify_tool = QgsMapToolIdentify(self.iface.mapCanvas())
        layers = QgsProject.instance().mapLayers().values()  # Get all layers
        results = identify_tool.identify(event.x(), event.y(), layers, QgsMapToolIdentify.TopDownAll)

        if not results:
            self.remove_highlight()
            return

        selected_result = None
        for result in results:
            if self.tool.check_if_feature_from_sketch_layer(result.mLayer.id()):
                selected_result = result
                break
            else:
                continue

        if selected_result:
            feature = selected_result.mFeature  # First identified feature
            layer = selected_result.mLayer
            fid = feature.id()
            code = feature.attribute("Code")
            self.remove_highlight()
            self.highlight_feature(layer, feature)
            self.tool.selected_attribute = dict(type=layer.name(), fid=fid, code=code)
            self.tool.update_selected_layer_style()
        else:
            self.remove_highlight()
            self.iface.messageBar().pushMessage("Info", "Selected feature does not belong to sketch layers.",
                                                level=Qgis.Warning, duration=5)

    def highlight_feature(self, layer, feature):
        """Based on the feature type, highlight the selected feature.
         If it is a point, add a vertex marker to the feature if it is either a polygon or a line, add a highlight.

         :param layer: Layer to add the highlight
         :type: QgsVectorLayer

         :param feature: Feature to add the highlight
         :type: QgsFeature
         """
        if "points" in layer.name():
            self.tool.vertex_marker = QgsVertexMarker(self.canvas)
            point_geom = feature.geometry().asPoint()
            self.tool.vertex_marker.setCenter(point_geom)
            self.tool.vertex_marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
            self.tool.vertex_marker.setIconSize(12)
            self.tool.vertex_marker.setColor(QColor(255, 38, 179, 255))
            self.tool.vertex_marker.setPenWidth(3)

        elif "polygons" in layer.name() or "lines" in layer.name():
            self.tool.highlight = QgsHighlight(self.canvas, feature.geometry(), layer)
            self.tool.highlight.setColor(QColor(255, 38, 179, 255))
            self.tool.highlight.setWidth(3)
            self.tool.highlight.setWidth(3)
            self.tool.highlight.setFillColor(QColor(255, 0, 0, 50))  # Lighter red fill
            self.tool.highlight.show()

    def remove_highlight(self):
        """Remove the highlight from the feature. If the highlight set is a highlight, then hide it, else if it is a
        vertex marker, then remove it."""
        if self.tool.highlight is not None:
            self.tool.highlight.hide()
            self.tool.highlight = None

        if self.tool.vertex_marker is not None:
            self.canvas.scene().removeItem(self.tool.vertex_marker)
            self.tool.vertex_marker = None