import bpy  # type: ignore
import bmesh #type: ignore
from ..constants import get_operator
from ..helpers.collider_helpers import quick_collision
class OBJECT_OT_MakeQuickCollision(bpy.types.Operator):
    bl_idname = get_operator("quick_collision")
    bl_label = "Make Quick Collisions"
    bl_options = {"REGISTER", "UNDO"}

    parent_collection = None

    def execute(self, context):
        parent_objects = [obj for obj in context.selected_objects]
        quick_collision(parent_objects, context)

        return {"FINISHED"}
    



