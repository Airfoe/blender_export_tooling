import bpy #type: ignore
from ..constants import get_operator
from ..constants import get_preferences
from pathlib import Path

class PATH_OT_FixAbsolutePaths(bpy.types.Operator):
    bl_idname = get_operator("fix_absolute_paths")
    bl_label = "Fix Absolute Paths"

    domain: bpy.props.StringProperty()#type: ignore
    anchor: bpy.props.StringProperty(default="\\PROD\\") #type: ignore


    def execute(self, context):
        self.prefix = get_preferences().root_directory

        if self.domain == "textures":
            self.fix_texture_paths()


        return {"FINISHED"}

    def fix_texture_paths(self):
        for image in bpy.data.images:
            corrected_path = self._replace_subpath(image.filepath)
            image.filepath = corrected_path


    def _replace_subpath(self, path: str) -> Path:
        try:
            idx = path.index(self.anchor)
            return self.prefix + path[idx:]        # keep the leading backslash, prepend X:
        except Exception as e:
            print(e)
            return path
