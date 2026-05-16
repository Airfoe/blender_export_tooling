import bpy #type: ignore
from ..constants import get_operator
class OBJECT_OT_SelectObject(bpy.types.Operator):
    bl_idname = get_operator("select")
    bl_label = "Select Object"
    bl_description = "Select the specified object"
    bl_options = {"REGISTER", "UNDO"}

    object_name: bpy.props.StringProperty(default="") #type: ignore

    def execute(self, context):
        current_mode = bpy.data.objects[self.object_name].select_get()
        if current_mode:
            bpy.data.objects[self.object_name].select_set(False)
            context.view_layer.objects.active = bpy.data.objects[self.object_name]
        else:
            if self.object_name in context.view_layer.objects:
                bpy.data.objects[self.object_name].select_set(True)
            else:
                self.report({"WARNING"}, "not in current scene")
        return {"FINISHED"}
