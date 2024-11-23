bl_info = {
    "name": "XML Object Importer",
    "blender": (2, 93, 0),
    "category": "Import-Export",
    "description": "Import objects defined in an XML file along with their transformations and models",
    "author": "Your Name",
    "version": (1, 0, 0),
    "warning": "",
    "tracker_url": "",
    "support": "COMMUNITY"
}

import bpy
import os
import xml.etree.ElementTree as ET
from bpy.props import StringProperty
from bpy.types import Operator, Panel, AddonPreferences

# Path to store the .obj folder location
class ImportXMLAddonPreferences(AddonPreferences):
    bl_idname = __name__

    obj_folder: StringProperty(
        name="OBJ Folder",
        description="Folder where the .obj files are located",
        default="",
        subtype='DIR_PATH'
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="XML Object Importer Preferences")
        layout.prop(self, "obj_folder")

# Function to load an object into Blender
def load_object(list_name, name, model, unit_config_name, x, y, z, scale_x, scale_y, scale_z, rotation_x, rotation_y, rotate_z, obj_folder):
    print(f"Loading object from {list_name} with id: {name}")
    print(f"\t Model name: {model}")
    print(f"\t UnitConfigName: {unit_config_name}")
    print(f"\t Location: {x}, {y}, {z}")
    print(f"\t Scale: {scale_x}, {scale_y}, {scale_z}")
    print(f"\t Rotation: {rotation_x}, {rotation_y}, {rotate_z}")
    
    # Try to find the .obj file using UnitConfigName first
    obj_file_path = os.path.join(obj_folder, unit_config_name + ".obj")
    
    if not os.path.exists(obj_file_path):
        # If not found, try using ModelName as fallback
        print(f"{unit_config_name}.obj not found, falling back to {model}.obj")
        obj_file_path = os.path.join(obj_folder, model + ".obj")
    
    if not os.path.exists(obj_file_path):
        print(f"Error: Neither {unit_config_name}.obj nor {model}.obj found!")
        return
    
    # Import the .obj file into the scene
    bpy.ops.import_scene.obj(filepath=obj_file_path)
    
    # Get the last imported object
    imported_obj = bpy.context.selected_objects[-1]
    
    # Rename the imported object to match the ModelName
    imported_obj.name = model  # Rename to the ModelName (instead of id)
    
    # Apply transformations
    imported_obj.location = (x, y, z)
    imported_obj.scale = (scale_x, scale_y, scale_z)
    
    # Set the rotation (convert degrees to radians)
    imported_obj.rotation_euler = (rotation_x * 3.14159 / 180, rotation_y * 3.14159 / 180, rotate_z * 3.14159 / 180)

# Function to read the XML file and return the root element
def read_xml_file(file_path):
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read()

        # Detect BOM and decode appropriately
        if raw_data.startswith(b'\xff\xfe'):  # UTF-16LE BOM
            xml_data = raw_data.decode('utf-16')
        elif raw_data.startswith(b'\xfe\xff'):  # UTF-16BE BOM
            xml_data = raw_data.decode('utf-16-be')
        elif raw_data.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
            xml_data = raw_data.decode('utf-8-sig')
        else:
            xml_data = raw_data.decode('utf-8')  # Default to UTF-8

        return ET.fromstring(xml_data)
    except Exception as e:
        print(f"Error reading XML file: {e}")
        return None

# Function to read a 3D vector (x, y, z) from the XML node
def read_vector3(node):
    x = float(node.find("T210[@N='X']").get("V"))
    y = float(node.find("T210[@N='Y']").get("V"))
    z = float(node.find("T210[@N='Z']").get("V"))
    return x, y, z

# Operator for importing the XML file and its objects
class IMPORT_XML_OT_Import(Operator):
    bl_idname = "import_scene.xml_import"
    bl_label = "Import XML Objects"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', name="XML File")

    def execute(self, context):
        preferences = context.preferences.addons[__name__].preferences
        obj_folder = preferences.obj_folder
        
        if not obj_folder:
            self.report({'ERROR'}, "No OBJ folder path set in preferences!")
            return {'CANCELLED'}
        
        xml_root = read_xml_file(self.filepath)
        if xml_root is None:
            self.report({'ERROR'}, "Failed to parse the XML file!")
            return {'CANCELLED'}

        # Process the XML and load all objects
        byml_root = xml_root.find("BymlRoot")
        scenario_root = byml_root.find("T192")
        
        for target_scenario in scenario_root:
            for obj_list in target_scenario:
                list_name = obj_list.get("N")
                for obj in obj_list:
                    try:
                        id = obj.find("T160[@N='Id']").get("V")
                        model = obj.find("T160[@N='ModelName']").get("V")
                        unit_config_name = obj.find("T160[@N='UnitConfigName']").get("V", model)  # Default to ModelName if UnitConfigName is missing
                        (x, y, z) = read_vector3(obj.find("T193[@N='Translate']"))
                        (s_x, s_y, s_z) = read_vector3(obj.find("T193[@N='Scale']"))
                        (r_x, r_y, r_z) = read_vector3(obj.find("T193[@N='Rotate']"))
                        
                        # Load the object into Blender
                        load_object(list_name, id, model, unit_config_name, x, y, z, s_x, s_y, s_z, r_x, r_y, r_z, obj_folder)
                    except Exception as e:
                        print(f"Error processing object: {e}")
                        continue

        return {'FINISHED'}

# Panel to add the operator to the import menu
class IMPORT_XML_PT_Panel(Panel):
    bl_label = "Import XML Objects"
    bl_idname = "IMPORT_XML_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Import"

    def draw(self, context):
        layout = self.layout
        preferences = context.preferences.addons[__name__].preferences
        layout.prop(preferences, "obj_folder")
        layout.operator("import_scene.xml_import", text="Import XML Objects")

# File Browser to select XML file
class IMPORT_XML_OT_FileSelect(Operator):
    bl_idname = "import_scene.xml_file_select"
    bl_label = "Select XML File"
    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        preferences = context.preferences.addons[__name__].preferences
        obj_folder = preferences.obj_folder

        if not obj_folder:
            self.report({'ERROR'}, "No OBJ folder path set in preferences!")
            return {'CANCELLED'}

        xml_root = read_xml_file(self.filepath)
        if xml_root is None:
            self.report({'ERROR'}, "Failed to parse the XML file!")
            return {'CANCELLED'}

        # Process the XML and load all objects
        byml_root = xml_root.find("BymlRoot")
        scenario_root = byml_root.find("T192")
        
        for target_scenario in scenario_root:
            for obj_list in target_scenario:
                list_name = obj_list.get("N")
                for obj in obj_list:
                    try:
                        id = obj.find("T160[@N='Id']").get("V")
                        model = obj.find("T160[@N='ModelName']").get("V")
                        unit_config_name = obj.find("T160[@N='UnitConfigName']").get("V", model)  # Default to ModelName if UnitConfigName is missing
                        (x, y, z) = read_vector3(obj.find("T193[@N='Translate']"))
                        (s_x, s_y, s_z) = read_vector3(obj.find("T193[@N='Scale']"))
                        (r_x, r_y, r_z) = read_vector3(obj.find("T193[@N='Rotate']"))
                        
                        # Load the object into Blender
                        load_object(list_name, id, model, unit_config_name, x, y, z, s_x, s_y, s_z, r_x, r_y, r_z, obj_folder)
                    except Exception as e:
                        print(f"Error processing object: {e}")
                        continue

        return {'FINISHED'}

# Register classes and add the import operator to the File menu
def menu_func_import(self, context):
    self.layout.operator(IMPORT_XML_OT_FileSelect.bl_idname, text="XML Object Importer (.xml)")

def register():
    bpy.utils.register_class(ImportXMLAddonPreferences)
    bpy.utils.register_class(IMPORT_XML_OT_FileSelect)
    bpy.utils.register_class(IMPORT_XML_PT_Panel)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportXMLAddonPreferences)
    bpy.utils.unregister_class(IMPORT_XML_OT_FileSelect)
    bpy.utils.unregister_class(IMPORT_XML_PT_Panel)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
