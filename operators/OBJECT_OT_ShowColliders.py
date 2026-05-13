import bpy #type: ignore
from ..constants import get_operator


class OBJECT_OT_ShowColliders(bpy.types.Operator):
    bl_idname = get_operator("show_colliders")
    bl_label = "Show Colliders"
    bl_description = "Select the specified object"
    bl_options = {"REGISTER", "UNDO"}

    hide: bpy.props.BoolProperty(default=True)#type: ignore

    def execute(self, context):

        if context.active_object in context.selected_objects:
            colliders = context.active_object.children
        else:
            colliders = context.scene.objects

        for obj in colliders:
            if obj.name.startswith("UCX_"):
                obj.hide_viewport = self.hide

        return {"FINISHED"}
