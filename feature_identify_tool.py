from qgis.core import QgsProject, QgsApplication
from qgis.gui import QgsMapTool, QgsMapMouseEvent
from PyQt5.QtCore import Qt

class FeatureIdentifyTool(QgsMapTool):
    def __init__(self, iface):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.setCursor(Qt.ArrowCursor)  # Keep normal cursor
        self.canvas.setMapTool(self)  # Activate the tool

    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        """Detects feature click in pan mode"""
        QgsApplication.messageLog().logMessage("FeatureIdentifyTool triggered", "DigitalSketchPlugin")

        layers = QgsProject.instance().mapLayers().values()  # Get all layers
        results = self.iface.mapCanvas().identify(event, layers, QgsMapTool.TopDownStop)

        if not results:
            QgsApplication.messageLog().logMessage("No feature clicked", "DigitalSketchPlugin")
            return

        feature = results[0].mFeature  # First identified feature
        layer = results[0].mLayer  # Corresponding layer
        fid = feature.id()
        attributes = feature.attributes()

        QgsApplication.messageLog().logMessage(f"Clicked on Layer: {layer.name()}, Feature ID: {fid}, Attributes: {attributes}", "DigitalSketchPlugin")