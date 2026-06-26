import bpy  # type: ignore
from .constants import get_operator


class Airfoe_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(context.scene.export_hook_settings, "export_type")
        box.prop(context.scene.export_hook_settings, "export_root_directory")


