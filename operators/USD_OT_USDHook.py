import bpy #type: ignore
import bpy.types #type: ignore
bpy.utils.expose_bundled_modules()
from pxr import UsdGeom, Sdf, Kind, UsdPhysics #type: ignore
from pxr import Usd #type: ignore
from pathlib import Path
import os
import time
from ..constants import get_operator, get_export_root, MAP_GEO_SUFFIX
from ..helpers import usd_helpers

EXPORT_ROOT = None

PURPOSE_ATTR = "userProperties:purpose"
VALID_PURPOSES = {"default", "render", "proxy", "guide"}

# Link assets as payloads rather than references. A reference makes USD parse
# and compose the whole target file at author time - 43 MB of prop geometry for
# a single map export. A payload on an unloaded stage costs nothing.
# Flip to False to go back to plain references if a consumer cannot load payloads.
LINK_AS_PAYLOAD = True


class USD_OT_USDHook(bpy.types.USDHook):
    bl_idname = get_operator('usd_hook')
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def on_export(export_context):
        global EXPORT_ROOT
        EXPORT_ROOT = get_export_root()
        settings = bpy.context.scene.export_hook_settings
        prim_map = export_context.get_prim_map()
        stage = export_context.get_stage()

        # Nothing this hook authors needs to see inside a linked asset, so keep
        # the stage unloaded: payloads then never get composed and the export
        # stops paying to parse every prop it points at. Load rules are session
        # state, they do not change what gets written.
        if LINK_AS_PAYLOAD:
            stage.SetLoadRules(Usd.StageLoadRules.LoadNone())

        t0 = time.perf_counter()
        linked, kept = link_assets(prim_map, stage)
        t1 = time.perf_counter()
        pruned = prune_unused_prototypes(stage)
        t2 = time.perf_counter()
        apply_prim_attributes(stage)
        t3 = time.perf_counter()
        set_material_tags(prim_map, stage)
        t4 = time.perf_counter()

        set_parent_class(stage, settings.parent_class)
        set_kind_assembly(stage)

        if settings.usd_asset_type == "scene":
            if settings.export_stage == "layout":
                link_map_geo(stage)
            elif settings.export_stage == "geo":
                set_map_tags(stage)
        t5 = time.perf_counter()

        print(f"[USDHook] link_assets:   {(t1 - t0) * 1000:7.1f} ms  ({linked} linked, {kept} kept inline)")
        print(f"[USDHook] prune_protos:  {(t2 - t1) * 1000:7.1f} ms  ({pruned} prototypes removed)")
        print(f"[USDHook] prim_attrs:    {(t3 - t2) * 1000:7.1f} ms")
        print(f"[USDHook] material_tags: {(t4 - t3) * 1000:7.1f} ms")
        print(f"[USDHook] stage_meta:    {(t5 - t4) * 1000:7.1f} ms")
        print(f"[USDHook] total:         {(t5 - t0) * 1000:7.1f} ms")


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


def apply_prim_attributes(stage):
    """Purpose, single-sidedness and collision in a single traversal.

    These used to be three separate passes over the whole stage, two of which
    read the same userProperties:purpose attribute.
    """
    prims = iter(Usd.PrimRange(stage.GetPseudoRoot()))
    for prim in prims:
        # Never author into a linked asset. Descending into a reference used to
        # stamp a redundant doubleSided override onto every mesh of every prop,
        # which the prop file already declares for itself.
        if prim.HasAuthoredReferences() or prim.HasAuthoredPayloads():
            prims.PruneChildren()

        if not prim.IsA(UsdGeom.Imageable):
            continue

        is_mesh = prim.IsA(UsdGeom.Mesh)
        if is_mesh:
            UsdGeom.Mesh(prim).CreateDoubleSidedAttr().Set(False)

        attr = prim.GetAttribute(PURPOSE_ATTR)
        purpose = attr.Get() if attr and attr.HasAuthoredValue() else None
        if not purpose:
            continue

        if purpose == "collision":
            # colliders ship as proxy geometry - "collision" is our own tag, not
            # a purpose token USD understands
            UsdGeom.Imageable(prim).CreatePurposeAttr().Set(UsdGeom.Tokens.proxy)
            if is_mesh:
                UsdPhysics.CollisionAPI.Apply(prim)
                UsdPhysics.MeshCollisionAPI.Apply(prim).CreateApproximationAttr().Set(UsdPhysics.Tokens.convexHull)
        elif purpose in VALID_PURPOSES:
            UsdGeom.Imageable(prim).CreatePurposeAttr().Set(purpose)


def link_assets(prim_map, stage):
    """Replace collection instances with a reference to the prop's own USD file.

    Iterates the prim map instead of the stage: the map only holds exported
    Blender datablocks, while a traversal walks every mesh, shader and prototype
    prim as well.
    """
    stage_dir = stage_directory(stage)
    linked = 0
    kept = 0

    for path, items in prim_map.items():
        if not items:
            continue

        obj = items[0]
        if not isinstance(obj, bpy.types.Object) or obj.type != "EMPTY":
            continue

        collection_name = usd_helpers.get_pending_link(obj.name)
        if collection_name is None:
            # instance the pre-export pass left alone because its target has not
            # been exported yet - its geometry is still inline here
            if obj.instance_type != "COLLECTION" or not obj.instance_collection:
                continue
            collection_name = obj.instance_collection.name

        prim = stage.GetPrimAtPath(path)
        if not prim or not prim.IsValid():
            continue

        if replace_with_reference(stage, prim, collection_name, stage_dir):
            linked += 1
        else:
            kept += 1

    return linked, kept


def clear_subtree(stage, prim):
    for child in prim.GetChildren():
        stage.RemovePrim(child.GetPath())


def stage_directory(stage):
    root_layer = stage.GetRootLayer()
    real_path = getattr(root_layer, "realPath", None) if root_layer else None
    if real_path:
        return os.path.dirname(real_path)
    return str(EXPORT_ROOT) if EXPORT_ROOT else os.getcwd()


def relative_asset_path(filepath, stage_dir):
    """USD asset paths are forward slashed, os.path.relpath is not."""
    try:
        relative = Path(os.path.relpath(str(filepath), start=stage_dir)).as_posix()
    except ValueError:
        # different drives on Windows, no relative path exists
        return Path(filepath).as_posix()
    return relative if relative.startswith(".") else f"./{relative}"


def author_link(prim, asset_path):
    """Point a prim at an external asset, as a payload where possible."""
    prim.GetReferences().ClearReferences()
    prim.GetPayloads().ClearPayloads()
    if LINK_AS_PAYLOAD:
        prim.GetPayloads().AddPayload(asset_path)
    else:
        prim.GetReferences().AddReference(asset_path)


def replace_with_reference(stage, prim, collection_name, stage_dir):
    filepath = usd_helpers.get_linked_prop_path(collection_name)
    if filepath is None:
        print(f"[USDHook] no exported USD for '{collection_name}', keeping inline geometry")
        return False

    clear_subtree(stage, prim)
    author_link(prim, relative_asset_path(filepath, stage_dir))
    return True


def prototype_scopes(stage):
    """Where Blender parks instance prototypes: either directly under the stage
    root or under the default prim, depending on root_prim_path."""
    roots = [stage.GetPseudoRoot()]
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid():
        roots.append(default_prim)

    scopes = []
    for root in roots:
        for child in root.GetChildren():
            if "prototype" in child.GetName().lower():
                scopes.append(child.GetPath())
    return scopes


def _internal_composition_targets(layer):
    """Prim paths something in this layer still points at internally.

    Read off the layer's authored specs rather than the composed stage: a
    composed traversal stops at instanceable prims, which is exactly what we
    need to see through here.
    """
    targets = set()

    def visit(spec):
        for list_op, is_asset_arc in (
            (spec.referenceList, True),
            (spec.payloadList, True),
            (spec.inheritPathList, False),
            (spec.specializesList, False),
        ):
            for items in (list_op.explicitItems, list_op.addedItems,
                          list_op.prependedItems, list_op.appendedItems,
                          list_op.orderedItems):
                for item in items:
                    if not is_asset_arc:
                        targets.add(str(item))
                    elif not item.assetPath and item.primPath:
                        # internal arc: points at a prim in this same layer
                        targets.add(str(item.primPath))

        for child in spec.nameChildren:
            visit(child)

    for child in layer.pseudoRoot.nameChildren:
        visit(child)

    return targets


def prune_unused_prototypes(stage):
    """Drop prototype geometry nothing references any more.

    Linking a collection instance clears its reference, which orphans the
    prototype it pointed at - but the prototype prims stay in the layer and get
    written to disk anyway. That is the "layout file still contains geometry"
    problem, so anything left unreferenced goes.
    """
    scopes = prototype_scopes(stage)
    if not scopes:
        return 0

    used = _internal_composition_targets(stage.GetRootLayer())
    removed = 0

    for scope_path in scopes:
        scope = stage.GetPrimAtPath(scope_path)
        if not scope or not scope.IsValid():
            continue

        for prototype in scope.GetChildren():
            prototype_path = str(prototype.GetPath())
            if any(t == prototype_path or t.startswith(prototype_path + "/") for t in used):
                continue
            stage.RemovePrim(prototype.GetPath())
            removed += 1

        scope = stage.GetPrimAtPath(scope_path)
        if scope and scope.IsValid() and not scope.GetChildren():
            stage.RemovePrim(scope_path)

    return removed


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
    author_link(geo_xform.GetPrim(), f"./{filename}")
    print(f"linked {filename} at {geo_xform.GetPrim().GetPath()}")


def set_material_tags(prim_map, stage):
    """Tag material prims so the engine knows which ones to rebuild as instances
    of an existing parent and which need a fresh one."""
    for path, items in prim_map.items():
        if not items:
            continue

        material = items[0]
        if not isinstance(material, bpy.types.Material):
            continue

        prim = stage.GetPrimAtPath(path)
        if not prim or not prim.IsValid():
            # material lived under a prototype or an instance we just replaced
            continue

        is_linked = material.library is not None
        prim.CreateAttribute("userProperties:MaterialInstanceParent", Sdf.ValueTypeNames.String).Set(
            material.name if is_linked else "MM_USD")
        prim.CreateAttribute("userProperties:CreateInstance", Sdf.ValueTypeNames.Bool).Set(not is_linked)
