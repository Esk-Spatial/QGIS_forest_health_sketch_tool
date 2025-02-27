import datetime

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
    notes_layer = gpkg_file.CreateLayer('notes', srs=spatial_ref, geom_type=ogr.wkbMultiLineString)

    for layer in [point_layer, polygon_layer, line_layer, notes_layer]:
        setup_layer_attr(layer)

    # Close dataset properly
    gpkg_file.FlushCache()
    gpkg_file = None  # Ensure proper closure

    return True  # Return True if successful

def setup_layer_attr(layer):
    # creating new fields
    layer.CreateField(ogr.FieldDefn("colour", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Shape", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Code", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("LAT", ogr.OFSTFloat32))
    layer.CreateField(ogr.FieldDefn("LON", ogr.OFSTFloat32))
    layer.CreateField(ogr.FieldDefn("Date", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Time", ogr.OFTString))

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

def split_array_to_chunks(items_list, chunk_size=3):
    return [items_list[i:i + chunk_size] for i in range(0, len(items_list), chunk_size)]


def adjust_color(hex_color, percent=30):
    """Adjusts a HEX color's brightness by a given percentage.

    Positive `percent` lightens the color.
    Negative `percent` darkens the color.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    factor = percent / 100

    r = min(255, max(0, int(r + (255 - r) * factor if factor > 0 else r * (1 + factor))))
    g = min(255, max(0, int(g + (255 - g) * factor if factor > 0 else g * (1 + factor))))
    b = min(255, max(0, int(b + (255 - b) * factor if factor > 0 else b * (1 + factor))))

    return f"#{r:02X}{g:02X}{b:02X}"

def get_current_date():
    return datetime.datetime.now().strftime('%x')

def get_current_time():
    return datetime.datetime.now().strftime('%X')