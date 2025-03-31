from qgis.core import QgsProject, QgsApplication, QgsMarkerSymbol
from qgis.gui import QgsMapTool, QgsMapMouseEvent, QgsMapToolIdentify, QgsHighlight
from PyQt5.QtCore import Qt
from qgis.PyQt.QtGui import QColor

class FeatureIdentifyTool(QgsMapTool):
    def __init__(self, iface, sketch_tool):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.setCursor(Qt.ArrowCursor)  # Keep normal cursor
        self.tool = sketch_tool

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        """Detects feature click in pan mode"""
        QgsApplication.messageLog().logMessage("FeatureIdentifyTool triggered", "DigitalSketchPlugin")
        identify_tool = QgsMapToolIdentify(self.iface.mapCanvas())
        layers = QgsProject.instance().mapLayers().values()  # Get all layers
        results = identify_tool.identify(event.x(), event.y(), layers, QgsMapToolIdentify.TopDownStopAtFirst)

        if not results:
            QgsApplication.messageLog().logMessage("No feature clicked", "DigitalSketchPlugin")
            return

        for result in results:
            feature = result.mFeature  # First identified feature
            layer = result.mLayer  # Corresponding layer
            fid = feature.id()
            # attributes = feature.attributes()
            if self.tool.highlight is not None:
                self.tool.highlight.hide()
            self.highlight_feature(layer, feature)
            self.tool.selected_attribute = dict(type=layer.name(), fid=fid)
            self.tool.update_selected_layer_style()

            QgsApplication.messageLog().logMessage(f"Layer: {layer.name()}, Feature ID: {fid}", "DigitalSketchPlugin")

    def highlight_feature(self, layer, feature):
        self.tool.highlight = QgsHighlight(self.canvas, feature.geometry(), layer)
        self.tool.highlight.setColor(QColor(255, 0, 0, 100))  # Red with 100 alpha (semi-transparent)
        self.tool.highlight.setWidth(3)
        if "points" in layer.name():
            point_size = 8  # Original point size, adjust as needed
            highlight_size = point_size * 1.5  # 50% larger

            # You can also use a different symbol altogether
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': 'red',
                'size': str(highlight_size),
                'outline_color': 'black',
                'outline_width': '0.5'
            })
            self.tool.highlight.setSymbol(symbol)

        elif "polygons" in layer.name() or "lines" in layer.name():
            self.tool.highlight.setFillColor(QColor(255, 0, 0, 50))  # Lighter red fill

        self.tool.highlight.show()