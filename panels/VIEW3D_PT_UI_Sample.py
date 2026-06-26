import bpy  # type: ignore
from pathlib import Path
from ..constants import AddonProperties
from ..operators.OBJECT_OT_ExportFBX import OBJECT_OT_ExportFBX
from ..operators.OBJECT_OT_ExportUSD import OBJECT_OT_ExportUSD
from ..operators.OBJECT_OT_ValidateUSD import OBJECT_OT_ValidateUSD
from ..operators.OBJECT_OT_FixWrongPurpose import OBJECT_OT_FixWrongPurpose
from ..operators.FILE_OT_SetAssetType import FILE_OT_SetAssetType
class VIEW3D_PT_UI_Sample(bpy.types.Panel):
    bl_label = "Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        layout = self.layout


        ################################
        ## FBX Export
        ################################

        box = layout.box()
        box.label(text="Export Static Mesh")
        column = box.column(align=True)
        column.scale_y = 1.5
        single = column.operator(OBJECT_OT_ExportFBX.bl_idname, text=f"Export as ({len(context.selected_objects)}) Files", icon="EXPORT")
        single.grouped = False
        single.selected = True

        grouped = column.operator(OBJECT_OT_ExportFBX.bl_idname, text="Export Selected as group", icon="EXPORT")
        grouped.grouped = True
        grouped.selected = True


        ################################
        ## USD Export
        ################################

        box = layout.box()
        box.label(text="Export Scene")
        column = box.column(align=True)
        column.scale_y = 1.5

        row = column.row()
        if not context.scene.export_hook_settings.usd_asset_type:
            row.operator(FILE_OT_SetAssetType.bl_idname, text = "Set as Asset", icon = "OBJECT_DATA").asset_type = "props"
            row.operator(FILE_OT_SetAssetType.bl_idname, text = "Set as Scene", icon = "SCENE_DATA").asset_type = "scene"

        else:
            row.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export", icon="EXPORT")

        if context.scene.export_hook_settings.usd_asset_type == "props":
            high_collection = context.scene.export_hook_settings.high_poly_collection
            coll_name = ""
            if high_collection:
                coll_name = high_collection.name
            export_high = row.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export High", icon="EXPORT")
            export_high.collection = coll_name
            box.prop(context.scene.export_hook_settings, "high_poly_collection", text="High Collection")


        column = box.column(align=True)
        column.scale_y = 1.5
        column.operator(OBJECT_OT_ValidateUSD.bl_idname, text=" Validate Scene", icon="INFO")
        box.prop(context.scene.export_hook_settings, "enable_export_usd_hook", text = "Export on save", toggle=True, icon="HOOK")
        box.label(text = f"Asset Type: {context.scene.export_hook_settings.usd_asset_type}")

