import bpy  # type: ignore
from ..constants import get_operator
from pathlib import Path

class OBJECT_OT_Export(bpy.types.Operator):
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
        if self.grouped:
            filename = Path(bpy.data.filepath).name.replace(".blend", "")
            self.export(filename)  
        else:
            selected_objects = context.selected_objects
            if not selected_objects:
                self.report({"ERROR"}, "No objects selected for export.")
                return {"CANCELLED"}
            
            for obj in selected_objects:
                #deselect all
                for all_obj in selected_objects:
                    all_obj.select_set(False)
                #select current
                obj.select_set(True)
                self.export(obj.name)


        return {"FINISHED"}



    def export(self, name):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({"ERROR"}, "Please save the blend file before exporting.")
            return
        export_path = Path(filepath).parent.parent / "export" / f"{name}.gltf"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=str(export_path),
            export_format='GLTF_SEPARATE',
            use_selection=self.selected,
            export_apply=True,
        )