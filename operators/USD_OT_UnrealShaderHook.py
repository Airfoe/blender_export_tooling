import bpy #type: ignore
from pxr import UsdShade, Sdf, Gf #type: ignore

r"""

/!\ Fully VibeCoded! Purely for convenience tho, materials get re-built in engine anyways /!\

Prompt:
Currently the materials do not survive because 
i am not directly using a principled BSDF (see picture). 
How hard is it to wire up the textures for USD in a USD Export hook?

(built by Claude Opus 4.8)

"""
def _unreal_group(mat):
    if not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.type == 'GROUP' and n.node_tree and "UnrealShader" in n.node_tree.name:
            return n
    return None

def _image_into(group, socket_name):
    """Walk back from a group input socket to the TEX_IMAGE feeding it."""
    sock = group.inputs.get(socket_name)
    if not sock or not sock.is_linked:
        return None
    node = sock.links[0].from_node
    while node and node.type != 'TEX_IMAGE':          # skip reroutes/converters
        linked = [s for s in node.inputs if s.is_linked]
        if not linked:
            return None
        node = linked[0].links[0].from_node
    return node.image if node and node.type == 'TEX_IMAGE' else None


class USD_OT_UnrealShaderHook(bpy.types.USDHook):
    bl_idname = "unreal_orm_usd_hook"
    bl_label = "Unreal ORM material export"

    @staticmethod
    def on_material_export(export_context, bl_material, usd_material):
        print("fired!")
        group = _unreal_group(bl_material)
        if group is None:
            return False        # not ours -> let Blender's normal path handle it

        stage = export_context.get_stage()
        mat = usd_material.GetPrim().GetPath()

        surf = UsdShade.Shader.Define(stage, mat.AppendChild("PreviewSurface"))
        surf.CreateIdAttr("UsdPreviewSurface")
        # This connection replaces any stub surface the exporter may have made.
        usd_material.CreateSurfaceOutput().ConnectToSource(surf.ConnectableAPI(), "surface")

        st = UsdShade.Shader.Define(stage, mat.AppendChild("stReader"))
        st.CreateIdAttr("UsdPrimvarReader_float2")
        st.CreateInput("varname", Sdf.ValueTypeNames.String).Set("st")   # or "UVMap"
        st_out = st.CreateOutput("result", Sdf.ValueTypeNames.Float2)

        def make_tex(name, image, colorspace):
            t = UsdShade.Shader.Define(stage, mat.AppendChild(name))
            t.CreateIdAttr("UsdUVTexture")
            # export_texture copies the file per the exporter's texture settings and
            # returns the asset path to reference. Confirm the arg for your Blender
            # version; fallback: bpy.path.abspath(image.filepath).
            path = export_context.export_texture(image)
            t.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(path)
            t.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(st_out)
            t.CreateInput("sourceColorSpace", Sdf.ValueTypeNames.Token).Set(colorspace)
            t.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
            t.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")
            return t

        # Base Color + Alpha (sRGB)
        bc = make_tex("baseColorTex", _image_into(group, "BaseColor"), "sRGB")
        surf.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
            bc.CreateOutput("rgb", Sdf.ValueTypeNames.Float3))
        surf.CreateInput("opacity", Sdf.ValueTypeNames.Float).ConnectToSource(
            bc.CreateOutput("a", Sdf.ValueTypeNames.Float))

        # ORM packed (raw): R=occlusion, G=roughness, B=metallic
        orm = make_tex("ormTex", _image_into(group, "ORM"), "raw")
        surf.CreateInput("occlusion", Sdf.ValueTypeNames.Float).ConnectToSource(
            orm.CreateOutput("r", Sdf.ValueTypeNames.Float))
        surf.CreateInput("roughness", Sdf.ValueTypeNames.Float).ConnectToSource(
            orm.CreateOutput("g", Sdf.ValueTypeNames.Float))
        surf.CreateInput("metallic", Sdf.ValueTypeNames.Float).ConnectToSource(
            orm.CreateOutput("b", Sdf.ValueTypeNames.Float))

        # Normal (raw + [0,1]->[-1,1] remap)
        nrm = make_tex("normalTex", _image_into(group, "Normal"), "raw")
        nrm.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(2, 2, 2, 1))
        nrm.CreateInput("bias", Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(-1, -1, -1, 0))
        surf.CreateInput("normal", Sdf.ValueTypeNames.Normal3f).ConnectToSource(
            nrm.CreateOutput("rgb", Sdf.ValueTypeNames.Float3))

        return True
