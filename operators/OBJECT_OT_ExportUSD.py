import bpy  # type: ignore
from ..constants import get_operator
from pathlib import Path
from ..helpers.usd_helpers import export_USD

class OBJECT_OT_ExportUSD(bpy.types.Operator):
    bl_idname = get_operator("export_usd")
    bl_label = "Export USD Operator"

    asset_type: bpy.props.StringProperty() #type: ignore

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({"ERROR"}, "Please save the blend file before exporting.")
            return {"CANCELLED"}

        filename = Path(bpy.data.filepath).stem
        export_USD(filename, context.scene.export_hook_settings.usd_asset_type)
        return {"FINISHED"}