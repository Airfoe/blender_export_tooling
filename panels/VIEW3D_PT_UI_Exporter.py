import bpy  # type: ignore
from pathlib import Path
from ..constants import AddonProperties
from ..operators.OBJECT_OT_ExportFBX import OBJECT_OT_ExportFBX
from ..operators.OBJECT_OT_ExportUSD import OBJECT_OT_ExportUSD
from ..operators.OBJECT_OT_ValidateUSD import OBJECT_OT_ValidateUSD
from ..operators.FILE_OT_SetAssetType import FILE_OT_SetAssetType
from ..project import paths, helpers
from ..project.asset_types import AssetType

class VIEW3D_PT_UI_Exporter(bpy.types.Panel):
    bl_label = "Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        layout = self.layout
        self.context = context

        ################################
        ## USD Export
        ################################

        box = layout.box()
        column = box.column(align=True)

        if not context.scene.export_hook_settings.usd_asset_type:
            column.scale_y = 1.5
            row = column.row(align=True)
            row.operator(FILE_OT_SetAssetType.bl_idname, text = "Set as Asset", icon = "OBJECT_DATA").asset_type = AssetType.PROPS.value
            row.operator(FILE_OT_SetAssetType.bl_idname, text = "Set as Scene", icon = "SCENE_DATA").asset_type = AssetType.SCENE.value



        if AssetType.of(context) is AssetType.PROPS:
            high_collection = context.scene.export_hook_settings.high_poly_collection
            coll_name = helpers.get_asset_name()
            if high_collection:
                coll_name = high_collection.name

            
            box.prop(context.scene.export_hook_settings, "high_poly_collection", text="High Collection")

            
            box.prop(context.scene.export_hook_settings, "parent_class", text = "Type")
            split = box.split(factor=0.5)
            split.scale_y = 1.5

            export_low = split.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export Low", icon="EXPORT")
            export_low.collection = coll_name
            export_low.file_name = helpers.get_asset_name()
            export_low.export_dir = paths.export_props_path

            export_high = split.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export High", icon="EXPORT")
            export_high.collection = coll_name
            export_high.file_name = helpers.get_asset_name() + "_high"
            export_high.export_dir = paths.export_props_path

        elif AssetType.of(context) is AssetType.SCENE:
            self.draw_scene_exports(layout=layout)



        column = box.column(align=True)
        column.scale_y = 1.5
        column.operator(OBJECT_OT_ValidateUSD.bl_idname, text="Validate Scene", icon="INFO")
        box.label(text = f"Asset Type: {AssetType.of(context).label}")



    def draw_scene_exports(self, layout):
        export_hook_settings = self.context.scene.export_hook_settings

        column = layout.column(align=True)
        split = column.split(factor=0.5)
        col = split.box()
        col.label(text="Geo")
        col.prop(export_hook_settings, "map_geo_collection", text = "")

        export_geo_op = col.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export", icon="EXPORT")
        if export_hook_settings.map_geo_collection:
            export_geo_op.collection = export_hook_settings.map_geo_collection.name
        else:
            export_geo_op.collection = ""

        export_geo_op.export_stage = "geo"
        export_geo_op.file_name = helpers.get_asset_name() + "_geo"
        export_geo_op.export_dir = paths.export_environment_path



        col = split.box()
        col.label(text="Layout")
        col.prop(export_hook_settings, "map_asset_collection", text = "")

        export_layout_op = col.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export", icon="EXPORT")
        if export_hook_settings.map_asset_collection:
            export_layout_op.collection = export_hook_settings.map_asset_collection.name 
        else:
            export_layout_op.collection = ""
        export_layout_op.export_stage = "layout"
        export_layout_op.file_name = helpers.get_asset_name()
        export_layout_op.export_dir = paths.export_environment_path



