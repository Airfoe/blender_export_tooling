import bpy #type: ignore
from ..constants import get_operator, is_usdview_installed, get_usdview_install_path
from pathlib import Path
import os
import subprocess

class USD_OT_PreviewUSD(bpy.types.Operator):
    bl_idname = get_operator("preview_usd")
    bl_label = "Preview USD File"

    file: bpy.props.StringProperty() #type: ignore

    def execute(self, context):

        if not is_usdview_installed():
            return {"CANCELLED"}

        self.launch_usdview()
        return {"FINISHED"}


    def launch_usdview(self):
        bat = get_usdview_install_path()      # ...\USDView\scripts\usdview.bat
        root = bat.parent.parent              # ...\USDView

        sysroot = os.environ.get("SystemRoot", r"C:\Windows")
        # A minimal, Blender-free environment. usdview.bat / set_usd_env.bat layer
        # USD's own PATH + add_dll_directory on top of this clean base.
        clean_env = {
            "SystemRoot": sysroot,
            "windir": sysroot,
            "COMSPEC": os.environ.get("COMSPEC", os.path.join(sysroot, "System32", "cmd.exe")),
            "PATHEXT": os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD"),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "NUMBER_OF_PROCESSORS": os.environ.get("NUMBER_OF_PROCESSORS", ""),
            "PROCESSOR_ARCHITECTURE": os.environ.get("PROCESSOR_ARCHITECTURE", ""),
            "PATH": os.pathsep.join([
                os.path.join(sysroot, "System32"),
                sysroot,
                os.path.join(sysroot, "System32", "Wbem"),
                os.path.join(sysroot, "System32", "WindowsPowerShell", "v1.0"),
            ]),
        }

        subprocess.Popen(
            ["cmd.exe", "/c", "call", str(bat), str(self.file)],
            cwd=str(root),
            env=clean_env,
        )