import bpy # type: ignore
from pathlib import Path
from time import sleep
from ..operators.OBJECT_OT_FixWrongPurpose import OBJECT_OT_FixWrongPurpose
import bmesh #type: ignore

def export_USD(name):
    filepath = bpy.data.filepath
    if not filepath:
        bpy.context.window_manager.report({"ERROR"}, "Please save the blend file before exporting.")
        return
    export_path = Path(filepath).parent.parent / "export" / f"{name}.usdc"
    export_path.parent.mkdir(parents=True, exist_ok=True)


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
        collection='', 
        rename_uvmaps=True, 

        only_deform_bones=False, 
        export_shapekeys=True, 
        use_instancing=False, 
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
        root_prim_path=f'/{name}_root', 
        export_custom_properties=True, 
        custom_properties_namespace='userProperties', 
        accessibility_label='', 
        accessibility_description='', 
        author_blender_name=True, 
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
        export_volumes=True, 

        triangulate_meshes=False, 
        quad_method='SHORTEST_DIAGONAL', 
        ngon_method='BEAUTY', usdz_downscale_size='KEEP', 
        usdz_downscale_custom_size=128, 
        merge_parent_xform=False, 
        convert_scene_units='CENTIMETERS', 
        meters_per_unit=100,
    )

    usd_post_processing(export_path)

def usd_post_processing(filepath):
    from pxr import Usd, UsdGeom #type: ignore
    stage = Usd.Stage.Open(str(filepath))
    filename = filepath.name

    valid_purposes = {"default", "render", "proxy", "guide"}

    # set purposes for colliders
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Imageable):

            attr = prim.GetAttribute("userProperties:purpose")
            purpose = attr.Get() if attr and attr.HasAuthoredValue() else None

            if purpose and purpose in valid_purposes:
                imageable = UsdGeom.Imageable(prim)
                imageable.CreatePurposeAttr().Set(purpose)

    stage.GetRootLayer().Save()

def send_usd_reload_request():
    import requests
    try:
        requests.post("http://127.0.0.1:5000/reload_usd")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Unreal Engine listener. Make sure Unreal Engine is running and the listener is set up correctly.")

def usd_validator(context):

    settings = context.scene.usd_validator_settings
    cache = settings.cache

    # ---------------------------------------
    # CLEAR OLD DATA
    # ---------------------------------------
    cache.missing_collision.clear()
    cache.missing_material.clear()
    cache.concave_colliders.clear()
    cache.wrong_purposes.clear()
    cache.wrong_data_names.clear()

    scene_valid = True

    # ---------------------------------------
    # SCAN SCENE
    # ---------------------------------------
    for obj in bpy.data.objects:

        if not obj:
            continue

        if obj.library:
            continue

        if obj.data and obj.data.library:
            continue


        if obj.type == 'MESH':
            if needs_collision(obj):

                item = cache.missing_collision.add()
                item.type = "missing_collision"
                item.object_name = obj.name
                item.expected = "collision mesh"
                item.found = ""
                item.message = f"{obj.name} is missing collision mesh"
                item.level = "WARNING"

            if needs_material(obj):

                item = cache.missing_material.add()
                item.type = "missing_material"
                item.object_name = obj.name
                item.expected = "material slot"
                item.found = "none"
                item.message = f"{obj.name} has no material"
                item.level = "WARNING"

            if is_collision_mesh(obj):
                conv = convexity(obj)
                if conv < 0.99:
                    item = cache.concave_colliders.add()
                    item.type = "concave_collision"
                    item.object_name = obj.name
                    item.expected = "< 0.95"
                    item.found = f"{conv:.23f}"
                    item.message = f"{obj.name} convexity is {conv:.2f}"
                    item.level = "ERROR"
                    scene_valid = False

                purpose = obj.get("purpose", "")

                if purpose != "proxy":
                    item = cache.wrong_purposes.add()
                    item.type = "wrong_purpose"
                    item.object_name = obj.name
                    item.expected = "proxy"
                    item.found = purpose
                    item.message = f"{obj.name} has wrong purpose: {purpose}"
                    item.level = "ERROR"

                    from ..operators.OBJECT_OT_FixWrongPurpose import OBJECT_OT_FixWrongPurpose
                    item.fix_operator = OBJECT_OT_FixWrongPurpose.bl_idname
                    item.fix_object_name = obj.name
                    item.fix_data = "proxy"
                    scene_valid = False

            if has_wrong_name(obj, "GEO"):
                from ..operators.OBJECT_OT_FixWrongDataName import OBJECT_OT_FixWrongDataName
                print(f"{obj.name} has wrong data name: {obj.data.name if obj.data else 'no data'}")
                item = cache.wrong_data_names.add()
                item.type = "wrong_name"
                item.object_name = obj.name
                item.expected = "GEO_ prefix for geometry objects"
                item.found = "no GEO_ prefix"
                item.message = f"{obj.name} does not follow naming convention. Expected name to start with GEO_"
                item.level = "WARNING"
                item.fix_operator = OBJECT_OT_FixWrongDataName.bl_idname
                item.fix_object_name = obj.name
                if is_collision_mesh(obj):
                    item.fix_data = "UXC"
                else:
                    item.fix_data = "GEO"
                
    
    return scene_valid

def needs_collision(obj):
    name = obj.name.lower()
    if is_collision_mesh(obj):
        return False
    
    for child in obj.children:
        if child.name.lower().startswith(f"ucx_{name}") or child.name.lower().startswith(f"ubx_{name}") or child.name.lower().startswith(f"usp_{name}"):
            return False
    return True

def needs_material(obj):
    if is_collision_mesh(obj):
        return False
    if len(obj.material_slots) == 0:
        return True
    return False

def is_collision_mesh(obj):
    name = obj.name.lower()
    if name.startswith(f"ucx_") or name.startswith(f"ubx_") or name.startswith(f"usp_"):
        return True
    return False

def has_wrong_name(obj, prefix_data):
    name = obj.name.lower()
    data_name = obj.data.name.lower() if obj.data else ""
    false_geo_name = not data_name.startswith(f"{prefix_data.lower()}_{name}")
    false_collider_name = not data_name.startswith(f"uxc_")
    return false_geo_name or false_collider_name


def convexity(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    
    original_volume = abs(bm.calc_volume())

    hull_bm = bm.copy()

    bmesh.ops.delete(
        hull_bm, 
        geom=hull_bm.faces[:] + hull_bm.edges[:], 
        context='FACES_ONLY'
    )

    bmesh.ops.convex_hull(
        hull_bm,
        input=hull_bm.verts
    )

    hull_bm.normal_update()
    hull_volume = abs(hull_bm.calc_volume())

    bm.free()
    hull_bm.free()

    # womp womp, stopid calculator cant divide by 0
    if hull_volume == 0:
        return 0
        
    print(original_volume / hull_volume)
    return original_volume / hull_volume