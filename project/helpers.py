import bpy  # type: ignore

def get_asset_name():
    return bpy.path.basename(bpy.data.filepath).split(".")[0]

def get_export_settings(context):
    return context.scene.export_hook_settings