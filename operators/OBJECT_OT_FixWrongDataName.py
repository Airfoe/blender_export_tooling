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

                if obj.name.startswith("UCX_"):
                    return {'FINISHED'}
                
                if obj.name.startswith(self.fix_data):
                    pass
                else:
                    obj.name = self.fix_data + obj.name 

                obj.data.name = f"{obj.name.removeprefix(self.fix_data)}"

                # fixing collision names too
                for index, children in enumerate(obj.children):
                    if children.name.startswith("UCX_"):
                        children.name = f"UCX_{obj.data.name}_{index:02d}"

            except Exception as e:
                self.report({"ERROR"}, f"{e}, liklely linked mesh?")

        from ..helpers.usd_helpers import usd_validator
        usd_validator(context)
        return {"FINISHED"}