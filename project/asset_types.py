from enum import Enum


class AssetType(str, Enum):
    NONE = ""
    PROPS = "props"
    SCENE = "scene"
    CHAR = "char"


    @property
    def label(self):
        return _META[self]["label"]

    @property
    def icon(self):
        return _META[self]["icon"]

    @property
    def folder(self):
        return _META[self]["folder"]

    @property
    def source_field(self):
        return _META[self]["source_field"]

    @property
    def export_field(self):
        return _META[self]["export_field"]

    @property
    def source_path(self):
        return self._resolve(self.source_field)

    @property
    def export_path(self):
        return self._resolve(self.export_field)

    def _resolve(self, field):
        if field is None:
            raise ValueError(f"{self.name} has no path field")
        from . import paths
        return paths.get(field)

    @classmethod
    def coerce(cls, value):
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
        "label": "Unset", 
        "icon": "QUESTION", 
        "folder": None,
        "source_field": None, 
        "export_field": None,
    },
    AssetType.PROPS: {
        "label": "Asset", 
        "icon": "OBJECT_DATA", 
        "folder": "Props",
        "source_field": "source_props_path", 
        "export_field": "export_props_path",
    },
    AssetType.SCENE: {
        "label": "Scene", 
        "icon": "SCENE_DATA", 
        "folder": "Environment",
        "source_field": "source_environment_path", 
        "export_field": "export_environment_path",
    },

    AssetType.CHAR:{
        "label": "Character", 
        "icon":"USER", "folder":"Chars", 
        "source_field": 
        "source_char_path", 
        "export_field": "export_char_path"
    }
}
