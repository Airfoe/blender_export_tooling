import bpy #type: ignore
from ..helpers.collider_helpers import quick_collision, apply_convex_hull

def fix_missing_collision(context, data):
    quick_collision([data["obj"]], context)

def fix_missing_material(context, data):
    pass

def fix_convex_collision(context, data):
    parent = data["parent"]
    obj = data["obj"]
    apply_convex_hull(context, obj)

def fix_wrong_purpose(context, data):
    pass

def fix_missing_prefix(context, data):
    pass

def fix_wrong_dataname(context, data):
    pass
