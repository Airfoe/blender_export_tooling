import bpy  # type: ignore
from ..constants import AddonProperties
from ..operators.OBJECT_OT_ExportFBX import OBJECT_OT_ExportFBX
from ..operators.OBJECT_OT_ExportUSD import OBJECT_OT_ExportUSD
from ..operators.OBJECT_OT_ValidateUSD import OBJECT_OT_ValidateUSD
from ..operators.OBJECT_OT_FixWrongPurpose import OBJECT_OT_FixWrongPurpose

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
        column.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export Scene", icon="EXPORT")
        column.prop(context.scene.export_hook_settings, "enable_export_usd_hook", text = "Export Scene on save", toggle=True, icon="HOOK")

        layout.operator(OBJECT_OT_ValidateUSD.bl_idname, text="Sample Operator", icon="INFO")
        layout.operator(OBJECT_OT_FixWrongPurpose.bl_idname, text="Fix Wrong Purpose", icon="INFO")

