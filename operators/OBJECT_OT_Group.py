import bpy  # type: ignore
from ..constants import get_operator


class OBJECT_OT_Group(bpy.types.Operator):
    bl_idname = get_operator("group")
    bl_label = "Group Objects"
    bl_options = {"REGISTER", "UNDO"}

    ungroup: bpy.props.BoolProperty(
        default=False
    )  # type: ignore

    group_name: bpy.props.StringProperty(
        default="GRP_Object"
    )  # type: ignore

    def execute(self, context):
        location = context.scene.cursor.location.copy()
        empty = bpy.data.objects.new(self.group_name, None)
        context.scene.collection.objects.link(empty)
        empty.location = location

        context.view_layer.objects.active = empty

        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
         

        return {"FINISHED"}