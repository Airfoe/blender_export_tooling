import os
from pathlib import Path

import bpy  # type: ignore

from ..constants import get_operator, get_export_root, MAP_GEO_SUFFIX
from ..helpers.usd_helpers import export_USD
from ..project import helpers


class OBJECT_OT_ExportUSD(bpy.types.Operator):
    bl_idname = get_operator("export_usd")
    bl_label = "Export USD Operator"

    collection: bpy.props.StringProperty()  # type: ignore
    export_dir: bpy.props.StringProperty()  # type: ignore
    export_stage: bpy.props.StringProperty() #type: ignore
    file_name: bpy.props.StringProperty() #type: ignore

    

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({"ERROR"}, "Please save the blend file before exporting.")
            return {"CANCELLED"}

        extension = helpers.get_export_settings(context).export_type
        export_path = Path(self.export_dir) / f"{self.file_name}.{extension}"
        export_path.parent.mkdir(parents=True, exist_ok=True)

        bpy.context.scene.export_hook_settings.export_stage = self.export_stage
        export_USD(
                export_path=export_path,
                root_name=self.file_name,
                export_collection=self.collection
            )
        self.collection = ""
        print(export_path)
        return {"FINISHED"}
