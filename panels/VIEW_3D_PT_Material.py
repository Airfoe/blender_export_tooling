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

        linked_materials, regular_materials = self.get_materials(objects)
        layout = self.layout
        box = layout.box()
        box.label(text="Library Materials")
        for material in linked_materials:
            box.label(text=material, icon = "ASSET_MANAGER")

        box = layout.box()
        box.label(text="New Materials")
        for material in regular_materials:
            box.label(text=material, icon = "MATERIAL")




    def get_materials(self, objects):
        linked_materials = []
        regular_materials = []
        for obj in objects:
            if obj.name.startswith("UCX_"):
                continue
            for slot in obj.material_slots:
                if slot.material:
                    name = slot.material.name
                    if slot.material.library:
                        if name not in linked_materials:
                            linked_materials.append(name)
                    else:
                        if name not in regular_materials:
                            regular_materials.append(name)

        return linked_materials, regular_materials