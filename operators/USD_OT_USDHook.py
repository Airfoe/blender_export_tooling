import bpy #type: ignore
import bpy.types #type: ignore
bpy.utils.expose_bundled_modules()
from pxr import UsdGeom #type: ignore
from pathlib import Path
import os
from ..constants import get_operator, get_export_root

class USD_OT_USDHook(bpy.types.USDHook):
    bl_idname = get_operator('usd_hook')
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def on_export(export_context):
        prim_map = export_context.get_prim_map()
        stage = export_context.get_stage()

        link_asset(prim_map, stage)
        set_usd_purpose(stage)

def set_usd_purpose(stage):

    valid_purposes = {"default", "render", "proxy", "guide"}

    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Imageable):
            continue

        imageable = UsdGeom.Imageable(prim)
        attr = prim.GetAttribute("userProperties:purpose")
        purpose = attr.Get() if attr and attr.HasAuthoredValue() else None
        if purpose and purpose in valid_purposes:
            imageable.CreatePurposeAttr().Set(purpose)

        if purpose and purpose == "collision":
            imageable.CreatePurposeAttr().Set("proxy")

def link_asset(prim_map, stage):
    to_replace = []
    
    for prim in stage.Traverse():
        items = prim_map.get(prim.GetPath())
        if not items:
            continue

        obj = items[0]

        if isinstance(obj, bpy.types.Object):
            if obj.type == "EMPTY" and obj.instance_type == "COLLECTION":
                to_replace.append((prim.GetPath(), obj))

        for path, obj in to_replace:
            prim = stage.GetPrimAtPath(path)

            if not prim.IsValid():
                continue

            success = safe_replace(stage, prim, obj.name)
            if success:
                print(f"Replaced payload at {path} with {obj.name}.usda")

def clear_subtree(stage, prim):
    for child in prim.GetChildren():
        stage.RemovePrim(child.GetPath())

def safe_replace(stage, prim, replacement):
    filepath = os.path.join(get_export_root(), "props", replacement, f"{replacement}.usda")
    if os.path.exists(filepath):
        clear_subtree(stage, prim)
        prim.GetReferences().ClearReferences()
        prim.GetReferences().AddReference(f"./props/{replacement}/{replacement}.usda")
    else:
        print(f"cant find {filepath}")
        return False