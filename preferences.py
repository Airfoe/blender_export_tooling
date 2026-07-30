import bpy  # type: ignore
from .constants import get_operator


class Airfoe_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    root_directory: bpy.props.StringProperty(subtype="DIR_PATH", default="X:\\")#type: ignore

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(context.scene.export_hook_settings, "export_type", text="USD File Format")
        box.prop(self, "root_directory", text = "Global Root Directory")
        box.prop(context.scene.export_hook_settings, "export_root_directory", "Export Directory")


