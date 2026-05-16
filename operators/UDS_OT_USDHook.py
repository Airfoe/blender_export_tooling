import bpy #type: ignore
import bpy.types #type: ignore
import textwrap #type: ignore

# Make `pxr` module available, for running as `bpy` PIP package.
bpy.utils.expose_bundled_modules()

import pxr.Usd as Usd #type: ignore 
import pxr.UsdGeom as UsdGeom #type: ignore 


from ..constants import get_operator

class UDS_OT_USDHook(bpy.types.USDHook):
    bl_idname = get_operator('usd_hook')
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def on_export(export_context):

        stage = export_context.get_stage()
        if stage is None:
            return False
        
        data = bpy.data
        if data is None:
            return False

        valid_purposes = {"default", "render", "proxy", "guide"}

        ucx_roots_to_delete = []

        for prim in stage.Traverse():
            if not prim.IsA(UsdGeom.Imageable):
                continue

            imageable = UsdGeom.Imageable(prim)

            attr = prim.GetAttribute("userProperties:purpose")
            purpose = attr.Get() if attr and attr.HasAuthoredValue() else None

            if purpose and purpose in valid_purposes:
                imageable.CreatePurposeAttr().Set(purpose)

            if purpose == "collision" and prim.IsA(UsdGeom.Xform):
                if not prim.GetName().startswith("UCX_"):
                    continue

                parent = prim.GetParent()
                if not parent:
                    continue

                mesh_children = [
                    c for c in prim.GetChildren()
                    if c.IsA(UsdGeom.Mesh)
                ]

                for mesh in mesh_children:
                    old_path = mesh.GetPath()
                    new_path = parent.GetPath().AppendChild(mesh.GetName())
                    stage.MovePrim(old_path, new_path)
                    new_prim = stage.GetPrimAtPath(new_path)
                    new_prim.SetMetadata("purpose", "proxy")

                ucx_roots_to_delete.append(prim.GetPath())

        for path in ucx_roots_to_delete:
            stage.RemovePrim(path)



        return True