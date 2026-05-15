import bpy  # type: ignore
import bmesh #type: ignore
from ..constants import get_operator

class OBJECT_OT_MakeQuickCollision(bpy.types.Operator):
    bl_idname = get_operator("quick_collision")
    bl_label = "Make Quick Collisions"
    bl_options = {"REGISTER", "UNDO"}

    parent_collection = None

    def execute(self, context):
        parent_objects = [obj for obj in context.selected_objects]
        for obj in parent_objects:
            if obj.type != "MESH":
                continue
            self.parent_collection = obj.users_collection[0]
            collider = self.make_collision(context,obj)
            self.set_as_colliders(context, obj, collider)
        return {"FINISHED"}
    

    def set_as_colliders(self, context, obj, collider):
        active_obj = obj
        old_and_new_colliders = []
        old_and_new_colliders.append(collider)
        for child in active_obj.children:
            if child.name.startswith("UCX_"):
                old_and_new_colliders.append(child)

        for index, collider in enumerate(old_and_new_colliders):
            if collider == active_obj:
                pass
            else:
                collider.name = f"UCX_{active_obj.name}_{index:02d}"
                collider.parent = active_obj
                collider.display_type = 'WIRE'
                collider["purpose"] = "proxy"
                collider.location = [0,0,0]
                collider.rotation_euler = [0,0,0]
                collider.scale = [1,1,1]


    def make_collision(self, context, obj):
        for sel_obj in context.selected_objects:
            sel_obj.select_set(False)

        new_obj = duplicate_object(obj)
        new_obj.select_set(False)


        bpy.context.view_layer.objects.active = new_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()
        bpy.ops.object.mode_set(mode='OBJECT')

        return new_obj


def duplicate_object(src):
    src = bpy.context.active_object
    new_obj = src.copy()
    new_obj.data = src.data.copy()
    bpy.context.collection.objects.link(new_obj)
    return new_obj