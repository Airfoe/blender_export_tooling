import bpy #type: ignore
from ..constants import get_operator

class OBJECT_OT_MarkAsPurpose(bpy.types.Operator):
    bl_idname = get_operator('MarkAsPurpose')
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    purpose: bpy.props.StringProperty()#type: ignore

    def execute(self, context):
        obj = context.active_object
        obj["purpose"] = self.purpose
        return {'FINISHED'}