
from qgis.gui import QgsMapTool
from qgis.core import QgsApplication

class CustomZoomTool(QgsMapTool):
    def __init__(self, iface, zoom_factor):
        super().__init__(iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.zoom_factor = zoom_factor

    def update_zoom_factor(self, zoom_factor):
        self.zoom_factor = zoom_factor

    def zoom_map(self, is_zoom_in):
        scale_factor = 1 / self.zoom_factor if is_zoom_in else self.zoom_factor
        self.canvas.zoomByFactor(scale_factor)