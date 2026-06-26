import bpy #type: ignore
from ..constants import get_operator
class OBJECT_OT_MakeCollider(bpy.types.Operator):
    bl_idname = get_operator("make_collider")
    bl_label = "Make Collider Objects"
    bl_description = "Select the specified object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        if len(context.selected_objects) < 2:
            return False
        return True

    def execute(self, context):
        active_obj = context.active_object
        old_and_new_colliders = []
        old_and_new_colliders.extend(context.selected_objects)
        for child in active_obj.children:
            if child.name.startswith("UCX_"):
                old_and_new_colliders.append(child)

        for index, collider in enumerate(old_and_new_colliders):
            if collider == active_obj:
                pass
            else:
                collider.name = f"UCX_{active_obj.name}_{index:02d}"
                collider.parent = active_obj
                collider.display_type = 'WIRE'
                collider["purpose"] = "proxy"
        return {"FINISHED"}