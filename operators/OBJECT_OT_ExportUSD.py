import os
from pathlib import Path

import bpy  # type: ignore

from ..constants import get_operator, get_export_root, MAP_GEO_SUFFIX
from ..helpers.usd_helpers import export_USD


class OBJECT_OT_ExportUSD(bpy.types.Operator):
    bl_idname = get_operator("export_usd")
    bl_label = "Export USD Operator"

    collection: bpy.props.StringProperty()  # type: ignore
    export: bpy.props.StringProperty() #type: ignore

    def execute(self, context):
        if not bpy.data.filepath:
            self.report({"ERROR"}, "Please save the blend file before exporting.")
            return {"CANCELLED"}

        settings = context.scene.export_hook_settings
        filetype = settings.export_type
        asset_type = settings.usd_asset_type
        stem = Path(bpy.data.filepath).stem


        if self.collection:
            export_collection = self.collection
            filename = f"{stem}_high.{filetype}"
        else:
            export_collection = stem
            filename = f"{stem}.{filetype}"

        export_root = get_export_root()
        export_dir = export_root
        os.makedirs(export_dir, exist_ok=True)

        export_path = os.path.join(export_dir, filename)


        if self.export == "GEO":
            if not settings.map_geo_collection:
                self.report({"ERROR"}, "Set the geo collection before exporting!")
                return {"CANCELLED"}

            geo_export_path = os.path.join(export_dir, f"{stem}{MAP_GEO_SUFFIX}.{filetype}")
            settings.export_stage = "geo"
            export_USD(
                export_path=geo_export_path,
                root_name=f"{stem}{MAP_GEO_SUFFIX}",
                export_collection=settings.map_geo_collection.name
            )
            self.report({'INFO'}, message = f"exported {export_collection} as {geo_export_path}")



        if self.export == "LAYOUT":
            settings.export_stage = "layout"
            if not settings.map_layout_collection:
                self.report({"ERROR"}, "Set the layout collection before exporting!")
                return {"CANCELLED"}

            export_USD(
                export_path=export_path,
                root_name=stem,
                export_collection=settings.map_asset_collection.name
            )
            self.report({'INFO'}, message = f"exported {export_collection} as {export_path}")


        self.collection = ""
        return {"FINISHED"}
