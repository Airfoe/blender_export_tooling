import bpy #type: ignore
from ..constants import get_operator
from ..helpers.collider_helpers import set_as_colliders
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
        set_as_colliders(context.active_object, context.selected_objects)
        return {"FINISHED"}
=======
        set_as_colliders(context.active_object, context.selected_objects)
        return {"FINISHED"}
>>>>>>> f9927923df2b44fa0ffec45a2d761c696cc70ab9
