import bpy  # type: ignore
from pathlib import Path
from ..constants import AddonProperties
from ..operators.OBJECT_OT_ExportFBX import OBJECT_OT_ExportFBX
from ..operators.OBJECT_OT_ExportUSD import OBJECT_OT_ExportUSD
from ..operators.OBJECT_OT_ValidateUSD import OBJECT_OT_ValidateUSD
from ..operators.FILE_OT_SetAssetType import FILE_OT_SetAssetType
class VIEW3D_PT_UI_Exporter(bpy.types.Panel):
    bl_label = "Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        layout = self.layout


        ################################
        ## FBX Export
        ################################

       #box = layout.box()
       #box.label(text="Export Static Mesh")
       #column = box.column(align=True)
       #column.scale_y = 1.5
       #single = column.operator(OBJECT_OT_ExportFBX.bl_idname, text=f"Export as ({len(context.selected_objects)}) Files", icon="EXPORT")
       #single.grouped = False
       #single.selected = True

       #grouped = column.operator(OBJECT_OT_ExportFBX.bl_idname, text="Export Selected as group", icon="EXPORT")
       #grouped.grouped = True
       #grouped.selected = True


        ################################
        ## USD Export
        ################################

        box = layout.box()
        column = box.column(align=True)

        if not context.scene.export_hook_settings.usd_asset_type:
            column.scale_y = 1.5
            row = column.row(align=True)
            row.operator(FILE_OT_SetAssetType.bl_idname, text = "Set as Asset", icon = "OBJECT_DATA").asset_type = "props"
            row.operator(FILE_OT_SetAssetType.bl_idname, text = "Set as Scene", icon = "SCENE_DATA").asset_type = "scene"



        if context.scene.export_hook_settings.usd_asset_type == "props":
            high_collection = context.scene.export_hook_settings.high_poly_collection
            coll_name = ""
            if high_collection:
                coll_name = high_collection.name

            
            box.prop(context.scene.export_hook_settings, "high_poly_collection", text="High Collection")

            
            box.prop(context.scene.export_hook_settings, "parent_class", text = "Type")
            split = box.split(factor=0.5)
            split.scale_y = 1.5
            export_low = split.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export Low", icon="EXPORT")
            export_high = split.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export High", icon="EXPORT")
            export_high.collection = coll_name
        
        elif context.scene.export_hook_settings.usd_asset_type == "scene":
            split = column.split(factor=0.5)
            col = split.box()
            col.label(text="GEO")
            col.prop(context.scene.export_hook_settings, "map_geo_collection", text = "")
            col.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export", icon="EXPORT").export = "GEO"

            col = split.box()
            col.label(text="Layout")
            col.prop(context.scene.export_hook_settings, "map_asset_collection", text = "")
            col.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export", icon="EXPORT").export = "LAYOUT"




        column = box.column(align=True)
        column.scale_y = 1.5
        column.operator(OBJECT_OT_ValidateUSD.bl_idname, text="Validate Scene", icon="INFO")
        box.label(text = f"Asset Type: {context.scene.export_hook_settings.usd_asset_type}")

