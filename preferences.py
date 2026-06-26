import bpy  # type: ignore
from .constants import get_operator


<<<<<<< HEAD
class Airfoe_Preferences(bpy.types.AddonPreferences):
=======
class Preferences(bpy.types.AddonPreferences):
>>>>>>> f9927923df2b44fa0ffec45a2d761c696cc70ab9
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        box = layout.box()
<<<<<<< HEAD
        box.prop(context.scene.export_hook_settings, "export_type")
        box.prop(context.scene.export_hook_settings, "export_root_directory")

=======
        box.label(text="Hello There!")
>>>>>>> f9927923df2b44fa0ffec45a2d761c696cc70ab9

