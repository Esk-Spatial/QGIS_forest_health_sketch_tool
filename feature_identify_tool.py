from qgis.core import QgsProject, QgsApplication
from qgis.gui import QgsMapTool, QgsMapMouseEvent, QgsMapToolIdentify
from PyQt5.QtCore import Qt

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
            self.tool.selected_attribute = dict(type=layer.name(), fid=fid)
            self.tool.update_selected_layer_style()

            QgsApplication.messageLog().logMessage(f"Layer: {layer.name()}, Feature ID: {fid}", "DigitalSketchPlugin")