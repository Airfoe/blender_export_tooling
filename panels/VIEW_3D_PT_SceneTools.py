import bpy  # type: ignore
from ..constants import AddonProperties

class VIEW3D_PT_SceneTools(bpy.types.Panel):
    bl_label = "Scene Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = AddonProperties.panel_category

    def draw(self, context):
        layout = self.layout
        self.draw_collider_tools(layout)


        from ..operators.OBJECT_OT_Group import OBJECT_OT_Group
        layout.operator(OBJECT_OT_Group.bl_idname)


        
    def draw_collider_tools(self, layout):
        from ..operators.OBJECT_OT_MakeCollider import OBJECT_OT_MakeCollider
        from ..operators.OBJECT_OT_ShowColliders import OBJECT_OT_ShowColliders


        box = layout.box()
        box.label(text= "Collider Tools")
        box.operator(OBJECT_OT_MakeCollider.bl_idname)

        row = box.row(align=True)
        row.operator(OBJECT_OT_ShowColliders.bl_idname, text = "Show Colliders", icon = "HIDE_OFF").hide = False
        row.operator(OBJECT_OT_ShowColliders.bl_idname, text = "Hide Colliders", icon = "HIDE_ON").hide = True

