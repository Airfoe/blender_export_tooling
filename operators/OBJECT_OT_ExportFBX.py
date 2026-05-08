import bpy  # type: ignore
from ..constants import get_operator
from pathlib import Path
from ..helpers.fbx_helpers import export_FBX_static

class OBJECT_OT_ExportFBX(bpy.types.Operator):
    bl_idname = get_operator("export")
    bl_label = "Export Operator"

    grouped : bpy.props.BoolProperty(
        name="Export as Group",
        description="Export selected objects as a group",
        default=False,
    )#type: ignore

    selected: bpy.props.BoolProperty(
        name="Export Selected",
        description="Export selected objects",
        default=True,
    )#type: ignore

    def execute(self, context):
        
        export_FBX_static(
            name=Path(bpy.data.filepath).stem, 
            selected=self.selected, 
            grouped=self.grouped)

        return {"FINISHED"}



