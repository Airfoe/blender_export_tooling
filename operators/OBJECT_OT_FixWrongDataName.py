import bpy #type: ignore
from ..constants import get_operator

class OBJECT_OT_FixWrongDataName(bpy.types.Operator):
    bl_idname = get_operator("fix_wrong_data_name")
    bl_label = "Fix Wrong Data Name"
    bl_description = "Attempt to fix objects with wrong data names"
    bl_options = {"REGISTER", "UNDO"}

    fix_data: bpy.props.StringProperty() #type:ignore
    object_name: bpy.props.StringProperty() #type:ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)
        if obj and obj.data:
            try:
                obj.data.name = f"{self.fix_data}_{obj.name}"
            except Exception as e:
                self.report({"ERROR"}, f"{e}, liklely linked mesh?")

        from ..helpers.usd_helpers import usd_validator
        usd_validator(context)
        return {"FINISHED"}