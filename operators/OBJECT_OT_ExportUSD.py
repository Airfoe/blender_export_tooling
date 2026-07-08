import os
from pathlib import Path

import bpy  # type: ignore

from ..constants import get_operator, get_export_root, MAP_GEO_SUFFIX
from ..helpers.usd_helpers import export_USD


class OBJECT_OT_ExportUSD(bpy.types.Operator):
    bl_idname = get_operator("export_usd")
    bl_label = "Export USD Operator"

    collection: bpy.props.StringProperty()  # type: ignore
    exporting_scene: bpy.props.BoolProperty(default = False) #type: ignore

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
        if self.exporting_scene:
            export_dir = export_root
        else:
            export_dir = os.path.join(export_root, asset_type, stem)
        os.makedirs(export_dir, exist_ok=True)

        export_path = os.path.join(export_dir, filename)


        if self.exporting_scene:
            if not settings.map_geo_collection or not settings.map_asset_collection:
                self.report({"ERROR"}, "Set the geo and assets collections before exporting a scene.")
                return {"CANCELLED"}

            # important: export geo first, so its ready to import into the next file
            geo_export_path = os.path.join(export_dir, f"{stem}{MAP_GEO_SUFFIX}.{filetype}")
            settings.export_stage = "geo"
            export_USD(
                export_path=geo_export_path,
                root_name=f"{stem}{MAP_GEO_SUFFIX}",
                export_collection=settings.map_geo_collection.name
            )
            settings.export_stage = "layout"

            export_USD(
                export_path=export_path,
                root_name=stem,
                export_collection=settings.map_asset_collection.name
            )

        else:
            export_USD(
                export_path=export_path,
                root_name=stem,
                export_collection=export_collection,
            )

        self.report({'INFO'}, message = f"exported {export_collection} as {filename}")
        self.collection = ""
        return {"FINISHED"}
