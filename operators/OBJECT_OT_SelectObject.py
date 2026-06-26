import bpy #type: ignore
from ..constants import get_operator
from ..helpers.generic_helper import ensure_object_selectable

class OBJECT_OT_SelectObject(bpy.types.Operator):
    bl_idname = get_operator("select")
    bl_label = "Select Object"
    bl_description = "Select the specified object"
    bl_options = {"REGISTER", "UNDO"}

    object_name: bpy.props.StringProperty(default="") #type: ignore

    def execute(self, context):
        if not self.object_name:
            self.object_name = "GEO_Cube"
        current_mode = bpy.data.objects[self.object_name].select_get()
        obj = bpy.data.objects[self.object_name]
        ensure_object_selectable(context, obj)
        if current_mode:
            obj.select_set(False)
            context.view_layer.objects.active = obj
        else:
            if self.object_name in context.view_layer.objects:
                obj.select_set(True)
            else:
                self.report({"WARNING"}, "not in current scene")
        return {"FINISHED"}
