import bpy # type: ignore
import os
import time
from pathlib import Path

from ..project import paths
from ..project.templates import TemplateError


# collection name -> Path of the already exported prop USD (or None).
# Only valid for the duration of one export, see clear_link_cache().
_link_path_cache = {}

# object name -> name of the collection it was instancing, filled in by
# _strip_linkable_instances() just before the exporter runs. The USD hook needs
# this because the object no longer carries an instance_collection at that point.
_pending_links = {}


def clear_link_cache():
    _link_path_cache.clear()
    _pending_links.clear()


def _prop_usd_candidates(collection_name):
    # {NAME} in the props template means "the asset this path belongs to", so it
    # has to resolve to the collection we are looking up - not to the currently
    # open .blend, which is the map itself.
    try:
        root = Path(paths.get("export_props_path", NAME=collection_name))
    except TemplateError as err:
        print(f"[usd] cannot resolve the prop export path: {err}")
        return []

    extensions = [bpy.context.scene.export_hook_settings.export_type, "usda", "usdc"]
    candidates = []
    for extension in extensions:
        candidate = root / f"{collection_name}.{extension}"
        if candidate not in candidates:
            candidates.append(candidate)
    return candidates


def get_linked_prop_path(collection_name):
    """Path of the already exported USD for `collection_name`, or None.

    Cached per export - a layout with hundreds of placements would otherwise
    stat the same handful of files hundreds of times.
    """
    if collection_name in _link_path_cache:
        return _link_path_cache[collection_name]

    result = None
    for candidate in _prop_usd_candidates(collection_name):
        if candidate.exists():
            result = candidate
            break

    _link_path_cache[collection_name] = result
    return result


def get_pending_link(object_name):
    """Collection this object instanced before the pre-export pass unhooked it."""
    return _pending_links.get(object_name)


def _objects_in_scope(export_collection):
    collection = bpy.data.collections.get(export_collection) if export_collection else None
    if collection:
        return list(collection.all_objects)
    return list(bpy.context.scene.objects)


def _strip_linkable_instances(export_collection):
    """Unhook collection instances that already exist as their own USD file.

    Without this the exporter evaluates and writes the full geometry of every
    instanced collection, which the USD hook then throws away and replaces with
    a reference. The empty still exports as an Xform carrying the placement, so
    the hook has a prim to attach the reference to.

    Instances whose target has not been exported yet are left alone: they still
    need their inline geometry.
    """
    stripped = []

    for obj in _objects_in_scope(export_collection):
        if obj.type != "EMPTY" or obj.instance_type != "COLLECTION":
            continue
        collection = obj.instance_collection
        if not collection or get_linked_prop_path(collection.name) is None:
            continue

        _pending_links[obj.name] = collection.name
        stripped.append((obj, collection))
        obj.instance_collection = None

    return stripped


def _restore_instances(stripped):
    for obj, collection in stripped:
        obj.instance_collection = collection


def export_USD(export_path, root_name, export_collection):

    t_start = time.perf_counter()

    import sys
    p4blender = sys.modules.get("p4blender")
    if p4blender is not None and p4blender.available():
        p4blender.checkout(export_path)
    t_checkout = time.perf_counter()

    clear_link_cache()
    stripped = _strip_linkable_instances(export_collection)
    if stripped:
        print(f"[usd] {len(stripped)} collection instances exported as links only")
    t_strip = time.perf_counter()

    try:
        bpy.ops.wm.usd_export(
            filepath=str(export_path),
            check_existing=True,
            filter_blender=False,
            filter_backup=False,
            filter_image=False,
            filter_movie=False,
            filter_python=False,
            filter_font=False,
            filter_sound=False,
            filter_text=False,
            filter_archive=False,
            filter_btx=False,
            filter_alembic=False,
            filter_usd=True,
            filter_obj=False,
            filter_volume=False,
            filter_folder=True,
            filter_blenlib=False,

            filemode=8,
            display_type='DEFAULT',
            sort_method='DEFAULT',
            filter_glob='*.usd',
            selected_objects_only=False,
            collection=export_collection,
            rename_uvmaps=True,

            only_deform_bones=False,
            export_shapekeys=True,
            use_instancing=True,
            evaluation_mode='RENDER',
            generate_preview_surface=True,
            generate_materialx_network=False,
            convert_orientation=True,
            export_global_forward_selection='X',
            export_global_up_selection='Z',
            export_textures_mode='NEW',
            overwrite_textures=False,
            relative_paths=True,
            xform_op_mode='TRS',
            root_prim_path=f'/{root_name}_root',
            export_custom_properties=True,
            custom_properties_namespace='userProperties',
            accessibility_label='',
            accessibility_description='',
            author_blender_name=False,
            convert_world_material=False,
            allow_unicode=True,

            export_animation=False,
            export_hair=False,
            export_uvmaps=True,
            export_mesh_colors=True,
            export_normals=True,
            export_materials=True,
            export_subdivision='BEST_MATCH',
            export_armatures=True,
            export_meshes=True,
            export_lights=True,
            export_cameras=True,
            export_curves=True,
            export_points=True,
            export_volumes=False,

            triangulate_meshes=True,
            quad_method='SHORTEST_DIAGONAL',
            ngon_method='BEAUTY', usdz_downscale_size='KEEP',
            usdz_downscale_custom_size=128,
            merge_parent_xform=True,
            convert_scene_units='METERS',
            meters_per_unit=100,
        )
        t_export = time.perf_counter()
    finally:
        _restore_instances(stripped)

    t_end = time.perf_counter()

    try:
        size = os.path.getsize(export_path) / (1024 * 1024)
        written = f"{size:.1f} MB"
    except OSError:
        written = "not written"

    print(f"[export]   p4 checkout:  {(t_checkout - t_start) * 1000:8.1f} ms")
    print(f"[export]   strip links:  {(t_strip - t_checkout) * 1000:8.1f} ms  ({len(stripped)} instances)")
    print(f"[export]   usd_export:   {(t_export - t_strip) * 1000:8.1f} ms  (includes the USDHook timings above)")
    print(f"[export]   restore:      {(t_end - t_export) * 1000:8.1f} ms")
    print(f"[export]   wrote {written} to {export_path}")



def send_usd_reload_request():
    import requests
    try:
        requests.post("http://127.0.0.1:5000/reload_usd")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Unreal Engine listener. Make sure Unreal Engine is running and the listener is set up correctly.")
