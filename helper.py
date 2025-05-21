import datetime

from delete_confirmation import DeleteConfirmationDialog

try:
    from osgeo import ogr
except ImportError:
    import ogr

try:
    from osgeo import osr
except ImportError:
    import osr

import platform

from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import QgsCoordinateTransform, QgsProject, QgsApplication, QgsLayerTreeGroup, QgsLayerTreeLayer, Qgis

def create_geopackage_file(path, iface, crs=None):
    """Create a new GeoPackage file with the given path and CRS

    :param path: Path to save the GeoPackage file to.
    :type path: str or pathlib.Path

    :param iface: QGIS interface object.
    :type iface: QgsInterface

    :param crs: CRS to use for the GeoPackage file. Defaults to EPSG:4326.
    :type crs: str, optional

    :return: True if the GeoPackage file was created successfully, False otherwise.
    """
    driver = ogr.GetDriverByName("GPKG")
    if driver is None:
        return False

    try:
        gpkg_file = driver.CreateDataSource(str(path))
        if gpkg_file is None:
            return False

        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromProj4(crs)

        # Create layers
        point_layer = gpkg_file.CreateLayer('sketch-points', srs=spatial_ref, geom_type=ogr.wkbPoint)
        polygon_layer = gpkg_file.CreateLayer('sketch-polygons', srs=spatial_ref, geom_type=ogr.wkbPolygon)
        line_layer = gpkg_file.CreateLayer('sketch-lines', srs=spatial_ref, geom_type=ogr.wkbMultiLineString)

        for layer in [point_layer, polygon_layer, line_layer]:
            setup_layer_attr(layer)

        # Close dataset properly
        gpkg_file.FlushCache()
        gpkg_file = None  # Ensure proper closure

        return True  # Return True if successful
    except Exception as e:
        QgsApplication.messageLog().logMessage(f"error: {e}", "DigitalSketchPlugin")
        iface.messageBar().pushMessage("Error", "Error Creating the GeoPackage File. Please try again with a different folder path.",
                                            level=Qgis.Critical, duration=5)
        return None


def setup_layer_attr(layer):
    """Setup layer attributes for the given layer

    :param layer: Layer to setup attributes for.
    :type layer: ogr.Layer
    """
    layer.CreateField(ogr.FieldDefn("colour", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Shape", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Code", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("LAT", ogr.OFSTFloat32))
    layer.CreateField(ogr.FieldDefn("LON", ogr.OFSTFloat32))
    layer.CreateField(ogr.FieldDefn("Surveyor", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Type", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Date", ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("Time", ogr.OFTString))

def get_closest_color_name(color):
    """Find the closest color name from the predefined QColor name

    :param color: QColor object to find the closest color name for.
    :type color: QColor

    :return: Closest color name as a string. If no match is found, return the hex value of the color.
    """
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

def split_array_to_chunks(items_list, chunk_size=2):
    """Split a list into chunks of a given size

    :param items_list: List to split into chunks.
    :type items_list: list

    :param chunk_size: Size of each chunk. Defaults to 2.
    :type chunk_size: int, optional

    :return: List of chunks.
    """
    return [items_list[i:i + chunk_size] for i in range(0, len(items_list), chunk_size)]


def adjust_color(hex_color, percent=30):
    """Adjusts a HEX color's brightness by a given percentage.

    Positive `percent` lightens the color.
    Negative `percent` darkens the color.

    :param hex_color: Hex color string to adjust.
    :type hex_color: str

    :param percent: Percentage to adjust the color by. Defaults to 30.
    :type percent: int, optional

    :return: Adjusted color string.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    factor = percent / 100

    r = min(255, max(0, int(r + (255 - r) * factor if factor > 0 else r * (1 + factor))))
    g = min(255, max(0, int(g + (255 - g) * factor if factor > 0 else g * (1 + factor))))
    b = min(255, max(0, int(b + (255 - b) * factor if factor > 0 else b * (1 + factor))))

    return f"#{r:02X}{g:02X}{b:02X}"

def get_current_date():
    """Get the current date in the format 'MM/DD/YYYY'

    :return: Current date in the format 'MM/DD/YYYY'
    """
    return datetime.datetime.now().strftime('%x')

def get_current_time():
    """Get the current time in the format 'HH:MM:SS'

    :return: Current time in the format 'HH:MM:SS'
    """
    return datetime.datetime.now().strftime('%X')

def update_feature_attributes(feature, layer_type, attributes):
    """Update feature attributes with the given attributes

    :param feature: Feature to update attributes for.

    :param layer_type: Type of layer the feature belongs to.

    :param attributes: Dictionary of attributes to update the feature with.

    :return: Updated feature with updated attributes.
    """
    geom = feature.geometry()
    if layer_type == 'points':
        point = geom.asPoint()
        lat, lon = point.y(), point.x()
    else:
        centroid = geom.centroid().asPoint()
        lat, lon = centroid.y(), centroid.x()
    colour_attr = attributes['colour'] if layer_type == 'polygons' else ''
    feature.setAttribute('colour', colour_attr)
    feature.setAttribute('shape', layer_type)
    feature.setAttribute('Code', attributes['code'])
    feature.setAttribute('LAT', f"{lat}")
    feature.setAttribute('LON', f"{lon}")
    feature.setAttribute('Surveyor', attributes['surveyor'])
    feature.setAttribute('Type', attributes['type_txt'])
    feature.setAttribute('Date', get_current_date())
    feature.setAttribute('Time', get_current_time())

    return feature

def show_delete_confirmation(text):
    """Show a confirmation dialog for deleting a Keypad category or element

    :param text: Text to display in the confirmation dialog.

    :return: Result of the confirmation dialog. True if the user confirms the deletion, False otherwise.
    """
    delete_confirmation =  DeleteConfirmationDialog(text)
    return delete_confirmation.exec_()

def reproject_to_destination_crs(geometry, source_crs, destination_crs):
    """Reproject a geometry to a destination CRS

    :param geometry: Geometry to reproject.

    :param source_crs: CRS of the geometry.

    :param destination_crs: Destination CRS to reproject the geometry to.

    :return: Reprojected geometry if no errors occurred, None otherwise.
    """
    transform = QgsCoordinateTransform(source_crs, destination_crs, QgsProject.instance())
    try:
        geometry.transform(transform)
    except Exception as e:
        QgsApplication.messageLog().logMessage(f'Geometry transform failed: {e}', 'DigitalSketchPlugin')
        return None

    return geometry

def get_existing_enabled_layers():
    """Get a dictionary of existing enabled layers in the QGIS project

    :return: Dictionary of existing enabled layers in the QGIS project.
    """
    existing_layers = QgsProject.instance().mapLayers(validOnly=True)
    layer_tree = QgsProject.instance().layerTreeRoot()
    enabled_layers = {
        l_id: layer
        for l_id, layer in existing_layers.items()
        if (layer_tree.findLayer(l_id) and
            layer_tree.findLayer(l_id).isVisible() and
            layer.__class__.__name__ == 'QgsVectorLayer') and
           "sketch-" in layer.name()
    }

    layer_groups = {
        'points': [],
        'polygons': [],
        'lines': []
    }

    for l_id, layer in enabled_layers.items():
        entry = {'name': layer.name(), 'layer': layer}
        if 'sketch-points' in layer.name():
            layer_groups['points'].append(entry)
        elif 'sketch-polygons' in layer.name():
            layer_groups['polygons'].append(entry)
        elif 'sketch-lines' in layer.name():
            layer_groups['lines'].append(entry)

    return layer_groups

def get_existing_layers():
    """Get a dictionary of existing layers in the QGIS project

    :return: Dictionary of existing layers in the QGIS project.
    """
    existing_layers = QgsProject.instance().mapLayers(validOnly=True)
    layer_tree = QgsProject.instance().layerTreeRoot()
    enabled_layers = {
        l_id: layer
        for l_id, layer in existing_layers.items()
        if (layer_tree.findLayer(l_id) and
            layer.__class__.__name__ == 'QgsVectorLayer') and
           "sketch-" in layer.name()
    }

    return enabled_layers

def get_bing_layer(name):
    """Get a Bing layer by its name

    :param name: Name of the Bing layer to get.

    :return: Bing layer if found, None otherwise.
    """
    existing_layers = QgsProject.instance().mapLayers()
    layer_tree = QgsProject.instance().layerTreeRoot()
    layer = {
        "l_id": l_id
        for l_id, layer in existing_layers.items()
        if (layer_tree.findLayer(l_id) and name == layer.name())
    }

    return layer

def get_default_button_height():
    """Get the default height of a button in pixels

    :return: Default height of a button in pixels.
    """
    return 26

def get_default_button_width():
    """Get the default width of a button in pixels

    :return: Default width of a button in pixels.
    """
    return 174

def get_default_button_font():
    """Get the default font for buttons

    :return: Default font for buttons.
    """
    system = platform.system()
    font = QFont()
    if system == 'Darwin':
        font.fromString(".AppleSystemUIFont,11,-1,5,50,0,0,0,0,0")
    else:
        font.fromString("MS Shell Dlg 2,11,-1,5,50,0,0,0,0,0")

    return font

def get_default_button_font_colour():
    """Get the default font colour for buttons

    :return: Default font colour for buttons.
    """
    return "#000000"

def get_default_auto_update_interval():
    """Get the default auto-update interval in seconds

    return: Default auto-update interval in seconds.
    """

    return 10