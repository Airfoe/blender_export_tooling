import bpy  # type: ignore
from bpy.props import BoolProperty, PointerProperty

# preferences
from .preferences import Sample_Preferences

# Operators
from .operators.OBJECT_OT_ValidateUSD import OBJECT_OT_ValidateUSD
from .operators.OBJECT_OT_ExportFBX import OBJECT_OT_ExportFBX
from .operators.OBJECT_OT_ExportUSD import OBJECT_OT_ExportUSD
from .operators.OBJECT_OT_SelectObject import OBJECT_OT_SelectObject
from .operators.OBJECT_OT_FixWrongPurpose import OBJECT_OT_FixWrongPurpose
from .operators.OBJECT_OT_FixWrongDataName import OBJECT_OT_FixWrongDataName
# panels
from .panels.VIEW3D_PT_UI_Sample import VIEW3D_PT_UI_Sample

# property groups
from .ValidatorPropertyGroup import (
    USDValidationItem,
    USDValidatorCache,
    USDValidatorSettings
)


# ---------------------------------------------------------
# ADDON SETTINGS (HOOK)
# ---------------------------------------------------------

class ExportHookSettings(bpy.types.PropertyGroup):

    enable_export_usd_hook: BoolProperty(
        name="Enable Export Hook",
        description="Toggle whether USD export runs automatically after saving the blend file.",
        default=False,
    ) #type: ignore


# ---------------------------------------------------------
# SAVE HANDLER
# ---------------------------------------------------------

@bpy.app.handlers.persistent
def export_usd_on_save(dummy):

    if not bpy.data.filepath:
        return

    scene = bpy.context.scene
    if not scene or not hasattr(scene, "export_hook_settings"):
        return

    if not scene.export_hook_settings.enable_export_usd_hook:
        return
    
    from .helpers.usd_helpers import usd_validator

    success = usd_validator(bpy.context)
    print("is scene valid?", success)
    if success:
        bpy.ops.airfoe.export_usd()
        from .helpers.usd_helpers import send_usd_reload_request
        send_usd_reload_request()
    else:
        bpy.ops.airfoe.validate_usd('INVOKE_DEFAULT')




# ---------------------------------------------------------
# CLASSES
# ---------------------------------------------------------

classes = [

    # preferences
    Sample_Preferences,

    # property groups
    USDValidationItem,
    USDValidatorCache,
    USDValidatorSettings,
    ExportHookSettings,

    # operators
    OBJECT_OT_ValidateUSD,
    OBJECT_OT_ExportFBX,
    OBJECT_OT_ExportUSD,
    OBJECT_OT_SelectObject,
    OBJECT_OT_FixWrongPurpose,
    OBJECT_OT_FixWrongDataName,

    # panels
    VIEW3D_PT_UI_Sample,
]


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.export_hook_settings = PointerProperty(
        type=ExportHookSettings
    )

    bpy.types.Scene.usd_validator_settings = PointerProperty(
        type=USDValidatorSettings
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

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# ---------------------------------------------------------
# DEV ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    register()