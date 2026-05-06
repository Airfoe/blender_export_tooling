import bpy  # type: ignore
from ..constants import AddonProperties
from ..operators.OBJECT_OT_Export import OBJECT_OT_Export
from ..operators.OBJECT_OT_ExportUSD import OBJECT_OT_ExportUSD

class VIEW3D_PT_UI_Sample(bpy.types.Panel):
    bl_label = "Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        column = box.column(align=True)
        column.scale_y = 1.5
        single = column.operator(OBJECT_OT_Export.bl_idname, text="Export Selected Individually", icon="EXPORT")
        single.grouped = False
        single.selected = True

        grouped = column.operator(OBJECT_OT_Export.bl_idname, text="Export Selected as group", icon="EXPORT")
        grouped.grouped = True
        grouped.selected = True

        box.prop(context.scene.export_hook_settings, "enable_export_hook", toggle=True, icon="HOOK")

        usd = column.operator(OBJECT_OT_ExportUSD.bl_idname, text="Export USD", icon="EXPORT")
