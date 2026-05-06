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
    )

    import requests
    try:
        requests.post("http://127.0.0.1:5000/reload")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Unreal Engine listener. Make sure Unreal Engine is running and the listener is set up correctly.")