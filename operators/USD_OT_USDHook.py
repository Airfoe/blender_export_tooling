import bpy #type: ignore
import bpy.types #type: ignore
bpy.utils.expose_bundled_modules()
from pxr import UsdGeom, Sdf, Kind, UsdPhysics #type: ignore
from pxr import Usd #type: ignore
from pathlib import Path
import os
import time
from ..constants import get_operator, get_export_root, MAP_GEO_SUFFIX

EXPORT_ROOT = None


class USD_OT_USDHook(bpy.types.USDHook):
    bl_idname = get_operator('usd_hook')
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def on_export(export_context):
        global EXPORT_ROOT
        EXPORT_ROOT = get_export_root()
        parent_class = bpy.context.scene.export_hook_settings.parent_class
        file_type = bpy.context.scene.export_hook_settings.usd_asset_type
        prim_map = export_context.get_prim_map()
        stage = export_context.get_stage()

        t0 = time.perf_counter()
        link_asset(prim_map, stage)
        t1 = time.perf_counter()
        set_usd_purpose(stage)
        set_parent_class(stage, parent_class)
        set_kind_assembly(stage)
        set_single_sided(stage)
        set_collision(stage)
        set_material_tag(prim_map, stage)


        export_stage = bpy.context.scene.export_hook_settings.export_stage
        if file_type == "scene":
            if export_stage == "layout":
                link_map_geo(stage)
            elif export_stage == "geo":
                set_map_tags(stage)


        t2 = time.perf_counter()
        print(f"[USDHook] link_asset:    {(t1 - t0) * 1000:.1f} ms")
        print(f"[USDHook] set_usd_purpose: {(t2 - t1) * 1000:.1f} ms")
        print(f"[USDHook] total hook:    {(t2 - t0) * 1000:.1f} ms")

def set_parent_class(stage, parent):
    root_prim = stage.GetDefaultPrim()
    if not root_prim or not root_prim.IsValid():
        return
    root_prim.CreateAttribute("userProperties:parentClass", Sdf.ValueTypeNames.Token).Set(parent)

def set_kind_assembly(stage):
    root_prim = stage.GetDefaultPrim()
    if not root_prim or not root_prim.IsValid():
        return
    Usd.ModelAPI(root_prim).SetKind(Kind.Tokens.assembly)

def set_usd_purpose(stage):
    valid_purposes = {"default", "render", "proxy", "guide", "collision"}

    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Imageable):
            continue

        imageable = UsdGeom.Imageable(prim)
        attr = prim.GetAttribute("userProperties:purpose")
        purpose = attr.Get() if attr and attr.HasAuthoredValue() else None
        if purpose and purpose in valid_purposes:
            imageable.CreatePurposeAttr().Set(purpose)


def link_asset(prim_map, stage):
    to_replace = []

    t_traverse_start = time.perf_counter()
    for prim in stage.Traverse():
        items = prim_map.get(prim.GetPath())
        if not items:
            continue

        obj = items[0]

        if isinstance(obj, bpy.types.Object):
            if obj.type == "EMPTY" and obj.instance_type == "COLLECTION":
                to_replace.append((prim.GetPath(), obj))
    t_traverse_end = time.perf_counter()

    t_replace_start = time.perf_counter()
    for path, obj in to_replace:

        prim = stage.GetPrimAtPath(path)

        if not prim.IsValid():
            continue

        if obj.instance_collection:
            success = safe_replace(stage, prim, obj.instance_collection.name)
            if success:
                print(f"Replaced payload at {path} with {obj.name}.usda")
    t_replace_end = time.perf_counter()

    print(f"[link_asset] traversal:   {(t_traverse_end - t_traverse_start) * 1000:.1f} ms  ({len(to_replace)} collection instances found)")
    print(f"[link_asset] replacements: {(t_replace_end - t_replace_start) * 1000:.1f} ms")

def clear_subtree(stage, prim):
    for child in prim.GetChildren():
        stage.RemovePrim(child.GetPath())

def safe_replace(stage, prim, replacement):
    filepath = os.path.join(EXPORT_ROOT, "props", replacement, f"{replacement}.usda")
    if os.path.exists(filepath):
        clear_subtree(stage, prim)
        prim.GetReferences().ClearReferences()
        prim.GetReferences().AddReference(f"./props/{replacement}/{replacement}.usda")
    else:
        print(f"cant find {filepath}")
        return False
    
def set_map_tags(stage):
    """Mark the geo file as map-owned so the importer can tell it apart from
    shared props."""
    root_prim = stage.GetDefaultPrim()
    if not root_prim or not root_prim.IsValid():
        return
    map_name = Path(bpy.data.filepath).stem
    root_prim.CreateAttribute("userProperties:assetScope", Sdf.ValueTypeNames.Token).Set("map")
    root_prim.CreateAttribute("userProperties:mapName", Sdf.ValueTypeNames.String).Set(map_name)


def link_map_geo(stage):
    """Reference the map geo file (exported just before this pass) at the
    origin of the layout file, exactly like a prop placement."""
    settings = bpy.context.scene.export_hook_settings
    stem = Path(bpy.data.filepath).stem
    filename = f"{stem}{MAP_GEO_SUFFIX}.{settings.export_type}"
    filepath = os.path.join(EXPORT_ROOT, filename)
    if not os.path.exists(filepath):
        print(f"cant find {filepath}")
        return

    root_prim = stage.GetDefaultPrim()
    if not root_prim or not root_prim.IsValid():
        return

    geo_xform = UsdGeom.Xform.Define(stage, root_prim.GetPath().AppendChild(f"{stem}{MAP_GEO_SUFFIX}"))
    # identity TRS like the prop placements author; the local ops also override
    # the geo root's own xform ops so orientation conversion isnt applied twice
    geo_xform.AddTranslateOp().Set((0.0, 0.0, 0.0))
    geo_xform.AddRotateXYZOp().Set((0.0, 0.0, 0.0))
    geo_xform.AddScaleOp().Set((1.0, 1.0, 1.0))
    geo_xform.GetPrim().GetReferences().AddReference(f"./{filename}")
    print(f"linked {filename} at {geo_xform.GetPrim().GetPath()}")


def set_single_sided(stage):
    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue

        mesh = UsdGeom.Mesh(prim)
        mesh.CreateDoubleSidedAttr().Set(False)


def set_collision(stage):
    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue
        attr = prim.GetAttribute("userProperties:purpose")
        if not (attr and attr.HasAuthoredValue() and attr.Get() == "collision"):
            continue
        UsdPhysics.CollisionAPI.Apply(prim)
        UsdPhysics.MeshCollisionAPI.Apply(prim).CreateApproximationAttr().Set(UsdPhysics.Tokens.convexHull)
        UsdGeom.Imageable(prim).CreatePurposeAttr().Set(UsdGeom.Tokens.proxy)

def set_material_tag(prim_map, stage):
    for prim in stage.Traverse():
        items = prim_map.get(prim.GetPath())
        if not items:
            continue

        obj = items[0]
        print("====")

        if isinstance(obj, bpy.types.Material):
            if obj.library:
                print(obj.name)
                prim.CreateAttribute("userProperties:MaterialInstanceParent", Sdf.ValueTypeNames.String).Set(obj.name)
                prim.CreateAttribute("userProperties:CreateInstance", Sdf.ValueTypeNames.Bool).Set(False)

            else:
                prim.CreateAttribute("userProperties:MaterialInstanceParent", Sdf.ValueTypeNames.String).Set("MM_USD")
                prim.CreateAttribute("userProperties:CreateInstance", Sdf.ValueTypeNames.Bool).Set(True)
