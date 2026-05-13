import bpy  # type: ignore
import bmesh #type: ignore
from ..constants import get_operator

class OBJECT_OT_MakeQuickCollision(bpy.types.Operator):
    bl_idname = get_operator("quick_collision")
    bl_label = "Make Quick Collisions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        parent_objects = [obj for obj in context.selected_objects]
        for obj in parent_objects:
            if obj.type != "MESH":
                continue
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

    def make_collision(self, context, obj):
        depsgraph = context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)

        mesh = bpy.data.meshes.new_from_object(obj_eval, preserve_all_data_layers = False, depsgraph=depsgraph)
        self.convex_hull_bmesh(mesh)
        collider = bpy.data.objects.new(f"UCX_{obj.name}", mesh)
        collider.parent = obj
        collider.matrix_world = obj.matrix_world.copy()
        context.scene.collection.objects.link(collider)
        collider.select_set(True)

        return collider


    def convex_hull_bmesh(self, mesh):
        new_bmesh = bmesh.new()
        new_bmesh.from_mesh(mesh)

        bmesh.ops.remove_doubles(new_bmesh, verts=new_bmesh.verts, dist=0.0001)

        bmesh.ops.convex_hull(new_bmesh, input=new_bmesh.verts)

        new_bmesh.to_mesh(mesh)
        new_bmesh.free()

        mesh.update()