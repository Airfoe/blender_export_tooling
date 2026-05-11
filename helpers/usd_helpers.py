import bpy # type: ignore
from pathlib import Path

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


def send_usd_reload_request():
    import requests
    try:
        requests.post("http://127.0.0.1:5000/reload_usd")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Unreal Engine listener. Make sure Unreal Engine is running and the listener is set up correctly.")

def usd_validator():
    pass