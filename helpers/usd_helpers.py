import bpy # type: ignore
from pathlib import Path
from time import sleep

def export_USD(name):
    filepath = bpy.data.filepath
    if not filepath:
        bpy.context.window_manager.report({"ERROR"}, "Please save the blend file before exporting.")
        return
    export_path = Path(filepath).parent.parent / "export" / f"{name}.usda"
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

    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Imageable):

            attr = prim.GetAttribute("userProperties:purpose")

            purpose = attr.Get() if attr and attr.HasAuthoredValue() else None

            if purpose:
                print("Found purpose:", purpose)

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

    missing_collision = []
    missing_triangulation = []
    missing_material = []
    concave_collidors = []

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if needs_collision(obj):
                missing_collision.append(obj)
            
            if needs_material(obj):
                missing_material.append(obj)

            if is_collision_mesh(obj) and not is_convex(obj):
                concave_collidors.append(obj)

            

    return_dict = {
        "missing_triangulation": missing_triangulation,
        "faulty_collisions": len(bpy.data.meshes),
        "missing_collisions": missing_collision,
        "missing_material": missing_material,
        "concave_collisions": concave_collidors,
    }
    return return_dict

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

def is_convex(obj):
    # Placeholder function to determine if a mesh is convex
    # In a real implementation, you would analyze the mesh geometry here
    return True