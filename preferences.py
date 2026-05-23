import bpy  # type: ignore
from .constants import get_operator


class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Hello There!")

