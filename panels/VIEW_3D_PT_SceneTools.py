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
        self.draw_misc_tools(layout, context)
        self.draw_helper_tools(layout, context)



    def draw_helper_tools(self, layout, context):
        from ..operators.PATH_OT_FixAbsolutePaths import PATH_OT_FixAbsolutePaths
        box = layout.box()
        box.label(text = "helpers")
        box.operator(PATH_OT_FixAbsolutePaths.bl_idname, text = "Fix Texture Paths", icon = "TEXTURE").domain = "textures"
        


    def draw_misc_tools(self, layout, context):
        from ..operators.OBJECT_OT_Group import OBJECT_OT_Group
        from ..operators.OBJECT_OT_MarkAsPurpose import OBJECT_OT_MarkAsPurpose
        from ..operators.FILE_OT_MakeAsset import FILE_OT_MakeAsset
        from ..operators.FILE_OT_OpenAsset import FILE_OT_OpenAsset

        box = layout.box()
        box.label(text="misc tools")
        box.operator(OBJECT_OT_Group.bl_idname)
        row = box.row(align=True)
        row.operator(OBJECT_OT_MarkAsPurpose.bl_idname, text = "guide").purpose = "guide"
        row.operator(OBJECT_OT_MarkAsPurpose.bl_idname, text = "render").purpose = "render"
        row.operator(OBJECT_OT_MarkAsPurpose.bl_idname, text = "proxy").purpose = "proxy"
        row.operator(OBJECT_OT_MarkAsPurpose.bl_idname, text = "clear").purpose = "default"

        obj = getattr(context, "active_object", None)

        if getattr(obj, "type", None) == "EMPTY" and getattr(obj, "instance_type", None) == "COLLECTION":
            box.operator(FILE_OT_OpenAsset.bl_idname, icon="FILE_ALIAS")
        else:
            box.operator(FILE_OT_MakeAsset.bl_idname, icon="BOOKMARKS")

                


        

        
    def draw_collider_tools(self, layout):
        from ..operators.OBJECT_OT_MakeCollider import OBJECT_OT_MakeCollider
        from ..operators.OBJECT_OT_ShowColliders import OBJECT_OT_ShowColliders
        from ..operators.OBJECT_OT_MakeQuickCollision import OBJECT_OT_MakeQuickCollision

        box = layout.box()
        box.label(text= "Collider Tools")
        box.operator(OBJECT_OT_MakeCollider.bl_idname)
        box.operator(OBJECT_OT_MakeQuickCollision.bl_idname)

        row = box.row(align=True)
        row.operator(OBJECT_OT_ShowColliders.bl_idname, text = "Show Colliders", icon = "HIDE_OFF").hide = False
        row.operator(OBJECT_OT_ShowColliders.bl_idname, text = "Hide Colliders", icon = "HIDE_ON").hide = True

