import bpy #type: ignore

from .generic_helper import run_isolated


def quick_collision(objects: list, context):
    for obj in objects:
        if obj.type != "MESH":
            continue
        collider = convex_hull_duplicate(context, obj)
        set_as_colliders(obj, [collider])



def set_as_colliders(obj, collider):
    active_obj = obj
    old_and_new_colliders = []
    old_and_new_colliders.extend(collider)
    for child in active_obj.children:
        if child.name.startswith("UCX_"):
            old_and_new_colliders.append(child)

    for index, collider in enumerate(old_and_new_colliders):
        if collider == active_obj:
            pass
        else:
            collider.name = f"UCX_{active_obj.data.name}_{index:02d}"
            collider.data.name = collider.name
            collider.parent = active_obj
            collider.display_type = 'WIRE'
            collider["purpose"] = "collision"
            collider.location = [0,0,0]
            collider.rotation_euler = [0,0,0]
            collider.scale = [1,1,1]


def convex_hull_duplicate(context, obj):
    new_obj = duplicate_object(obj)
    apply_convex_hull(context, new_obj)
    return new_obj


def apply_convex_hull(context, obj):

    def isolation():
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()
    run_isolated(context, isolation, obj, [obj], mode="EDIT")



def duplicate_object(src):
    new_obj = src.copy()
    new_obj.data = src.data.copy()
    bpy.context.collection.objects.link(new_obj)
    return new_obj