# paths.py
import bpy  # type: ignore
from pathlib import Path
from ..constants import get_preferences
from .templates import resolve, TemplateError

TOKENS = {
    "ROOT":     ("Project root",        lambda: get_preferences().root_directory),
    "NAME": ("Current .blend name", lambda: Path(bpy.data.filepath).stem or "AssetName"),
}

PATH_FIELDS = (
    "source_environment_path", 
    "source_props_path", 
    "source_char_path",

    "export_environment_path", 
    "export_props_path", 
    "export_char_path",
)



# /!\ Claude Opus 5 /!\:
def build_context():
    return {k: fn() for k, (_desc, fn) in TOKENS.items()}


def get(field):
    """Resolve one preference path field. Raises TemplateError."""
    return resolve(getattr(get_preferences(), field), build_context())


def __getattr__(name):
    if name in PATH_FIELDS:
        return get(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")