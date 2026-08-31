from enum import Enum


class AssetType(str, Enum):
    NONE = ""
    PROPS = "props"
    SCENE = "scene"
    CHAR = "char"

    # Without this, str(AssetType.PROPS) and f"{AssetType.PROPS}" render as
    # "AssetType.PROPS" instead of "props" on Python 3.11 (Blender's version).
    __str__ = str.__str__


    @property
    def label(self):
        return _META[self]["label"]

    @property
    def icon(self):
        return _META[self]["icon"]

    @property
    def folder(self):
        """Directory name this kind lives under in the 3D source tree."""
        return _META[self]["folder"]

    @property
    def source_field(self):
        return _META[self]["source_field"]

    @property
    def export_field(self):
        return _META[self]["export_field"]

    @property
    def source_path(self):
        """Resolved source path for this kind. Raises TemplateError."""
        return self._resolve(self.source_field)

    @property
    def export_path(self):
        """Resolved export path for this kind. Raises TemplateError."""
        return self._resolve(self.export_field)

    def _resolve(self, field):
        if field is None:
            raise ValueError(f"{self.name} has no path field")
        # imported lazily: project.paths reaches back into constants
        from . import paths
        return paths.get(field)

    @classmethod
    def coerce(cls, value):
        """Never raise on unknown stored values - old or hand-edited .blend
        files should degrade to "unset", not break the UI."""
        if isinstance(value, cls):
            return value
        try:
            return cls(value or "")
        except ValueError:
            return cls.NONE

    @classmethod
    def of(cls, context):
        return cls.coerce(context.scene.export_hook_settings.usd_asset_type)

    @classmethod
    def items(cls, include_none=False):
        """Item tuples for bpy.props.EnumProperty."""
        members = [m for m in cls if include_none or m is not cls.NONE]
        return [(m.value, m.label, f"{m.label} asset", m.icon, i)
                for i, m in enumerate(members)]


_META = {
    AssetType.NONE: {
        "label": "Unset", "icon": "QUESTION", "folder": None,
        "source_field": None, "export_field": None,
    },
    AssetType.PROPS: {
        "label": "Asset", "icon": "OBJECT_DATA", "folder": "Props",
        "source_field": "source_props_path", "export_field": "export_props_path",
    },
    AssetType.SCENE: {
        "label": "Scene", "icon": "SCENE_DATA", "folder": "Environment",
        "source_field": "source_environment_path", "export_field": "export_environment_path",
    },

    AssetType.CHAR:{
        "label": "Character", "icon":"USER", "folder":"Chars", 
        "source_field": "source_char_path", "export_field": "export_char_path"
    }
}
