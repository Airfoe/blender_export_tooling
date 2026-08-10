import os
from pathlib import Path

import bpy  # type: ignore

from ..constants import get_operator, get_export_root, MAP_GEO_SUFFIX
from ..helpers.usd_helpers import export_USD


class OBJECT_OT_ExportUSD(bpy.types.Operator):
    bl_idname = get_operator("export_usd")
    bl_label = "Export USD Operator"

    collection: bpy.props.StringProperty()  # type: ignore
    relative_path: bpy.props.StringProperty()  # type: ignore
    export_stage: bpy.props.StringProperty() #type: ignore
    file_name: bpy.props.StringProperty() #type: ignore

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({"ERROR"}, "Please save the blend file before exporting.")
            return {"CANCELLED"}

        root_path = get_export_root()
        export_path = Path(root_path) / self.relative_path

        bpy.context.scene.export_hook_settings.export_stage = self.export_stage
        export_USD(
                export_path=export_path,
                root_name=self.file_name,
                export_collection=self.collection
            )
        self.collection = ""
        print(export_path)
        return {"FINISHED"}
