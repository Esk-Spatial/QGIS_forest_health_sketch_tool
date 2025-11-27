![icon.png](icon.png) 
# QGIS Digital Sketch Mapping Tool

Sketch Mapping Tool is a plugin built for QGIS using Python, PYQGIS and QT. This Plugin works on QGIS platforms with Qt5.\
This plugin allows digitising polygons, lines and points on the map. Integrates with QGIS's built-in GPS services.

## Installation
### Method 1 Plugin Repository (Recommended)
1. Open Settings tab in **Manage and Install Plugins**
2. Click **Add** and add the following details:
   - **Name:** ESK Repo
   - **URL:** http://qgis.eskspatial.com.au/plugins/plugins.xml
3. Go to **All** tab and search for "Digital Sketch Mapping Tool"

### Method 2 Cloning the repository
Clone the repo into the following location and restart QGIS:
#### Windows:
```markdown
%AppData%\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```
#### MacOS:
```markdown
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```
After installation, restart QGIS and enable the plugin through **Manage and Install Plugins**.

## Deploying to a repository
This section is for administrators who want to host their own QGIS plugin repository.
### Apache Config
Add the following to a Apache config file 
```conf
<VirtualHost *:80 >
ServerAdmin server.admin@email.com
ServerName serverName
DocumentRoot path/to/plugins/directory
ErrorLog ${APACHE_LOG_DIR}/qgiserror.log
CustomLog "${APACHE_LOG_DIR}/qgisaccess.log" common

# Optional: Ensure proper MIME type for XML files
AddType application/xml .xml

<Directory path/to/plugins/directory>
Options Indexes FollowSymLinks
AllowOverride None
Require all granted
</Directory>
</VirtualHost>
```
Replace `path/to/plugins/directory` witht the actual path to your repository directory

### Repository/'Folder Structure
Create the following structure in your repository directory:
```
repository/
├── plugins.xml
└── data/
    └── digital_sketch_mapping_tool.zip
```

```xml
<?xml version="1.0"?>
<plugins>
    <pyqgis_plugin name="Digital Sketch Mapping Tool" version="1.0.0">
        <description>{description}</description>
        <qgis_minimum_version>3.4</qgis_minimum_version>
        <file_name>digital_sketch_mapping_tool.zip</file_name>
        <author_name>ESK Spatial</author_name>
        <email>developer@eskspatial.com.au</email>
        <download_url>http://qgis.eskspatial.com.au/plugins/data/digital_sketch_mapping_tool.zip</download_url>
    </pyqgis_plugin>
</plugins>
```
**Important*** When publishing a new version increment the version number in the version attribute.\
Updated the Author details as well.

### Developed By:
**ESK Spatial**\
***developer@eskspatial.com.au***

