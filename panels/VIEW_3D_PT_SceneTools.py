import bpy  # type: ignore
from ..constants import AddonProperties
from ..operators.OBJECT_OT_MakeCollider import OBJECT_OT_MakeCollider


class VIEW3D_PT_SceneTools(bpy.types.Panel):
    bl_label = "Scene Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_MakeCollider.bl_idname)