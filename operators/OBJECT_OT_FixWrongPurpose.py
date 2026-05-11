import bpy # type: ignore
from ..constants import get_operator


class OBJECT_OT_FixWrongPurpose(bpy.types.Operator):
    bl_idname = get_operator("fix_wrong_purpose")
    bl_label = "Fix Wrong Purpose"
    bl_description = "Attempt to fix objects with wrong purposes"
    bl_options = {"REGISTER", "UNDO"}

    new_purpose: bpy.props.StringProperty() #type:ignore
    object_name: bpy.props.StringProperty() #type:ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)
        if obj:
            obj["purpose"] = self.new_purpose

        from ..helpers.usd_helpers import usd_validator
        usd_validator(context)
        return {"FINISHED"}