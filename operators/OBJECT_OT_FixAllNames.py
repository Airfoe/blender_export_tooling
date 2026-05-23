import bpy  # type: ignore
from ..constants import get_operator
from ..scene_validation.rules import is_collision_mesh

class OBJECT_OT_FixAllNames(bpy.types.Operator):
    bl_idname = get_operator("fix_all_names")
    bl_label = "Fixes all names"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.scene.objects:
            if is_collision_mesh(obj):
                pass

            obj.name = obj.name.removeprefix("GEO_")


        return {"FINISHED"}