import bpy # type: ignore
from pathlib import Path


def export_FBX_static(name, selected=False, grouped=False):

    scene_state = fbx_validator()
    if not scene_state:
        return scene_state

    if selected:
        objects_to_export = bpy.context.selected_objects
    else:
        objects_to_export = bpy.data.objects
    
    if grouped:
        FBX_ExportOperation(name, selected=False)
    else:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_export:
            obj.select_set(True)
            FBX_ExportOperation(obj.name, selected=True)
            obj.select_set(False)

    return True


def FBX_ExportOperation(name, selected=False):
    filepath = bpy.data.filepath
    if not filepath:
        bpy.context.window_manager.report({"ERROR"}, "Please save the blend file before exporting.")
        return
    export_path = Path(filepath).parent.parent / "export" / f"{name}.fbx"
    export_path.parent.mkdir(parents=True, exist_ok=True)


    bpy.ops.export_scene.fbx(
        filepath=str(export_path), 
        check_existing=True, 
        filter_glob='*.fbx', 
        use_selection=selected, 
        use_visible=False, 
        use_active_collection=False, 
        collection='', 
        global_scale=1.0, 
        apply_unit_scale=True, 
        apply_scale_options='FBX_SCALE_NONE', 
        use_space_transform=True, 
        bake_space_transform=False, 
        object_types={
            'MESH', 
            }, 
        use_mesh_modifiers=True, 
        use_mesh_modifiers_render=True, 
        mesh_smooth_type='OFF', 
        colors_type='SRGB', 
        prioritize_active_color=False, 
        use_subsurf=False, 
        use_mesh_edges=False, 
        use_tspace=False, 
        use_triangles=False, 
        use_custom_props=False, 
        embed_textures=True, 
        batch_mode='OFF', 
        use_batch_own_dir=True, 
        use_metadata=True, 
        axis_forward='X', 
        axis_up='Z'
        )
    
    send_fbx_reload_request(str(export_path), generate_content_path(str(export_path)))


def send_fbx_reload_request(filepath, content_path):
    import requests
    try:
        response = requests.post(
            f"http://127.0.0.1:5000/import_fbx",
            json={
                "filepath": filepath,
                "content_path": content_path
            }
        )

        print("Status:", response.status_code)
        print("Response:", response.json())

    except requests.exceptions.ConnectionError as e:
        print("Connection error:", e)

def fbx_validator():
    return True
    pass

def generate_content_path(filepath):
    import os
    if not filepath:
        bpy.context.window_manager.report({"ERROR"}, "Please save the blend file before exporting.")
        return None

    content_prefix = "/Game/03-Art"
    suffix = filepath.split("3D")[1]
    suffix_folder = os.path.dirname(suffix)
    return os.path.join(content_prefix, suffix_folder)