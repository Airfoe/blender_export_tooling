# i like to put values i need in multiple places here so i can change them in one place
import bpy  # type: ignore
import os
import tomllib # type: ignore


# has to be all lowercase
bl_id_prefix = "airfoe"

# suffix for the geo usd file a scene export writes next to the map file
MAP_GEO_SUFFIX = "_geo"

class AddonProperties:
    module_name = __package__
    panel_category = "Airfoe"


def get_manifest():
    toml_path = os.path.join(os.path.dirname(__file__), "blender_manifest.toml")
    with open(toml_path, "rb") as f:
        manifest = tomllib.load(f)
    return manifest

def is_usdview_installed():
    usdview = get_usdview_install_path()
    if os.path.isfile(usdview):
        return True
    else:
        print(f"USDView not installed at {usdview}")
        return False

def get_usdview_install_path():
    from pathlib import Path
    install_path = get_preferences().usdview_path
    usdview = Path(install_path) / "USDView" / "scripts" /  "usdview.bat"
    return usdview


def get_export_root():
    from pathlib import Path
    root_path = bpy.context.scene.export_hook_settings.export_root_directory
    return Path(root_path)

def get_asset_type(context):
    from .project.asset_types import AssetType
    return AssetType.of(context)

def get_preferences():
    # No context needed, directly get addon preferences by package name
    addon_prefs = bpy.context.preferences.addons.get(__package__).preferences
    return addon_prefs


def get_operator(name):
    return bl_id_prefix + "." + name.lower()