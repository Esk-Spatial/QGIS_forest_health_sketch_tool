
from qgis.gui import QgsMapTool
from qgis.core import QgsApplication

class CustomZoomTool(QgsMapTool):
    """Tool to zoom in and out of the map"""
    def __init__(self, iface, zoom_factor):
        """Constructor.

        :param iface: QGIS interface object.
        :type iface: QgsInterface

        :param zoom_factor: Zoom factor to use when zooming in or out.
        :type zoom_factor: float
        """
        super().__init__(iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.zoom_factor = zoom_factor

    def update_zoom_factor(self, zoom_factor):
        """Update the zoom factor used when zooming in or out.

        :param zoom_factor: Zoom factor to use when zooming in or out.
        :type zoom_factor: float
        """
        self.zoom_factor = zoom_factor

    def zoom_map(self, is_zoom_in):
        """Zoom in or out of the map.

        :param is_zoom_in: True if zooming in, False if zooming out.
        :type is_zoom_in: bool
        """
        scale_factor = 1 / self.zoom_factor if is_zoom_in else self.zoom_factor
        self.canvas.zoomByFactor(scale_factor)