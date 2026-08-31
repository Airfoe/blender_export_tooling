import bpy #type: ignore
from ..constants import get_operator
from ..project.asset_types import AssetType
import os


class FILE_OT_SetAssetType(bpy.types.Operator):
    bl_idname = get_operator('SetAssetType')
    bl_label = "Sets the Asset Type"
    bl_options = {'REGISTER', 'UNDO'}

    asset_type: bpy.props.EnumProperty(items=AssetType.items()) #type: ignore
    asset_name: bpy.props.StringProperty() #type: ignore

    @property
    def kind(self):
        return AssetType.coerce(self.asset_type)

    def invoke(self, context, event):
        if bpy.data.filepath == '':
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "asset_name", text=f"{self.kind.label} name")


    def execute(self, context):
        kind = self.kind
        if kind is AssetType.NONE:
            self.report({'ERROR'}, "No asset type given")
            return {'CANCELLED'}

        filepath = kind.source_path
        os.makedirs(filepath, exist_ok=True)
        path = os.path.join(filepath, f"{self.asset_name}.blend")

        if bpy.data.filepath == '':
            bpy.ops.wm.save_mainfile(filepath = path)

        context.scene.export_hook_settings.usd_asset_type = kind.value
        return {'FINISHED'}
