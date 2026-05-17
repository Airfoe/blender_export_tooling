import bpy #type: ignore
from ..constants import get_operator

class FILE_OT_SetAssetType(bpy.types.Operator):
    bl_idname = get_operator('SetAssetType')
    bl_label = "Sets the Asset Type"
    bl_options = {'REGISTER', 'UNDO'}

    asset_type: bpy.props.StringProperty() #type: ignore

    def execute(self, context):
        context.scene.export_hook_settings.usd_asset_type = self.asset_type
        return {'FINISHED'}