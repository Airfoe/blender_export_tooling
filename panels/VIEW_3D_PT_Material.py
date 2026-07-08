import bpy  # type: ignore
from pathlib import Path
from ..constants import AddonProperties

class VIEW3D_PT_UI_Material(bpy.types.Panel):
    bl_label = "Material Assignment"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        export_coll_name = Path(bpy.data.filepath).stem
        collection = bpy.data.collections.get(export_coll_name)
        objects = collection.all_objects if collection else []

        if not objects:
            return
        layout = self.layout

        for obj in objects:
            if obj.name.startswith("UCX_"):
                continue
            box = layout.box()
            box.label(text=f"{obj.name}", icon = 'MESH_CUBE')
            col = box.column(align=True)
            for slot in obj.material_slots:
                if slot.material:
                    row = col.row(align=True)
                    if slot.material.library:
                        row.label(text=f"{slot.material.name}", icon = 'LINKED')
                    else:
                        row.label(text=f"{slot.material.name}", icon = 'MATERIAL')
                    row.prop(context.scene.usd_validator_settings, "shaders")