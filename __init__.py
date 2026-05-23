import bpy  # type: ignore
from bpy.props import BoolProperty, PointerProperty

from .ValidatorPropertyGroup import USD_PG_ValidatorSettings, USD_PG_ExportHookSettings
from .generated_classes import CLASSES


@bpy.app.handlers.persistent
def export_usd_on_save(dummy):

    if not bpy.data.filepath:
        return

    scene = bpy.context.scene
    if not scene or not hasattr(scene, "export_hook_settings"):
        return

    if not scene.export_hook_settings.enable_export_usd_hook:
        return
    
    from .scene_validation.validator import scene_validator

    success = True
    print("is scene valid?", success)
    if success:
        bpy.ops.airfoe.export_usd()
        from .helpers.usd_helpers import send_usd_reload_request
        send_usd_reload_request()
    else:
        bpy.ops.airfoe.validate_usd('INVOKE_DEFAULT')


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.export_hook_settings = PointerProperty(
        type=USD_PG_ExportHookSettings
    )

    bpy.types.Scene.usd_validator_settings = PointerProperty(
        type=USD_PG_ValidatorSettings
    )

    handlers = bpy.app.handlers.save_post
    if export_usd_on_save not in handlers:
        handlers.append(export_usd_on_save)


# ---------------------------------------------------------
# UNREGISTER
# ---------------------------------------------------------

def unregister():
    handlers = bpy.app.handlers.save_post
    while export_usd_on_save in handlers:
        handlers.remove(export_usd_on_save)

    if hasattr(bpy.types.Scene, "export_hook_settings"):
        del bpy.types.Scene.export_hook_settings

    if hasattr(bpy.types.Scene, "usd_validator_settings"):
        del bpy.types.Scene.usd_validator_settings

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()