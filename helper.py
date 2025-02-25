import os

try:
    from osgeo import ogr
except ImportError:
    import ogr

try:
    from osgeo import osr
except ImportError:
    import osr

from qgis.PyQt.QtGui import QColor

def create_geopackage_file(path, crs=None):

    driver = ogr.GetDriverByName("GPKG")
    if driver is None:
        return False

    gpkg_file = driver.CreateDataSource(str(path))
    if gpkg_file is None:
        return False

    spatial_ref = osr.SpatialReference()
    if crs is not None:
        spatial_ref.ImportFromProj4(crs)
    else:
        spatial_ref.ImportFromEPSG(4326)  # WGS 84

    # Create layers
    point_layer = gpkg_file.CreateLayer('points', srs=spatial_ref, geom_type=ogr.wkbPoint)
    polygon_layer = gpkg_file.CreateLayer('polygons', srs=spatial_ref, geom_type=ogr.wkbPolygon)
    line_layer = gpkg_file.CreateLayer('lines', srs=spatial_ref, geom_type=ogr.wkbLineString)

    for layer in [point_layer, polygon_layer, line_layer]:
        setup_layer_attr(layer)

    # Close dataset properly
    gpkg_file.FlushCache()
    gpkg_file = None  # Ensure proper closure

    return True  # Return True if successful

def setup_layer_attr(layer):
    # creating new fields
    layer.CreateField(ogr.FieldDefn("colour", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("label", ogr.OFTString))

    def get_closest_color_name(self, color):
        """Find the closest color name from predefined QColor names"""
        min_distance = float('inf')
        closest_color_name = None
        for name in QColor.colorNames():
            named_color = QColor(name)
            distance = (
                               (color.red() - named_color.red()) ** 2 +
                               (color.green() - named_color.green()) ** 2 +
                               (color.blue() - named_color.blue()) ** 2
                       ) ** 0.5  # Euclidean distance in RGB space

            if distance < min_distance:
                min_distance = distance
                closest_color_name = name

        return closest_color_name if closest_color_name else color.name()  # Return hex if no match