# paths.py
import bpy  # type: ignore
from pathlib import Path
from ..constants import get_preferences
from .templates import resolve, TemplateError
from .asset_types import AssetType

TOKENS = {
    "ROOT":     ("Project root",        lambda: get_preferences().root_directory),
    "NAME": ("Current .blend name", lambda: Path(bpy.data.filepath).stem),
}

# /!\ Claude Opus 5 /!\:
PATH_FIELDS = tuple(
    field
    for kind in AssetType
    for field in (kind.source_field, kind.export_field)
    if field
)



def build_context():
    return {k: fn() for k, (_desc, fn) in TOKENS.items()}


def get(field, **overrides):
    """Resolve one preference path field. Raises TemplateError.

    Overrides replace tokens for this call only, e.g.
    get("export_props_path", NAME="Catapult") to point at another asset's
    export folder instead of the currently open file's.
    """
    ctx = build_context()
    ctx.update({key.upper(): value for key, value in overrides.items()})
    return resolve(getattr(get_preferences(), field), ctx)


def __getattr__(name):
    if name in PATH_FIELDS:
        return get(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")