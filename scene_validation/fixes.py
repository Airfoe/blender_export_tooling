import bpy  # type: ignore

from ..helpers.collider_helpers import quick_collision, apply_convex_hull
from .core import fixer
from .rules import DATA_PREFIXES, is_collision_mesh, parent_base_name


@fixer("create_collision")
def create_collision(context, obj):
    quick_collision([obj], context)


@fixer("make_convex")
def make_convex(context, obj):
    apply_convex_hull(context, obj)


@fixer("set_collision_purpose")
def set_collision_purpose(context, obj):
    obj["purpose"] = "collision"


@fixer("clear_purpose")
def clear_purpose(context, obj):
    if "purpose" in obj:
        del obj["purpose"]


@fixer("rename_collider")
def rename_collider(context, obj):
    if obj.parent is None:
        return
    base = obj.name[:4].upper() + parent_base_name(obj.parent)
    obj.name = free_collider_name(base)
    if obj.data:
        obj.data.name = obj.name


@fixer("sync_data_name")
def sync_data_name(context, obj):
    if is_collision_mesh(obj):
        obj.data.name = obj.name
        return
    prefix = DATA_PREFIXES.get(obj.type, "")
    obj.data.name = obj.name.removeprefix(prefix)

@fixer("unparent_keep_transform")
def unparent_keep_transform(context, obj):
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = world


# Helpers

def free_collider_name(base):
    """First unused UE style collider name: <base>_00, <base>_01, ..."""
    index = 0
    while f"{base}_{index:02d}" in bpy.data.objects:
        index += 1
    return f"{base}_{index:02d}"
