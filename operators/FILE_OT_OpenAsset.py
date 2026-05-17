import bpy #type: ignore
from ..constants import get_operator
from pathlib import Path

class FILE_OT_OpenAsset(bpy.types.Operator):
    bl_idname = get_operator('OpenAsset')
    bl_label = "Open Asset"
    bl_options = {'REGISTER', 'UNDO'}


    save: bpy.props.BoolProperty(default=True)#type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "save", expand = True, text = f"Save {Path(bpy.data.filepath).name} before opening?")

    def execute(self, context):

        obj = context.active_object
        collection = obj.instance_collection
        collection_name = collection.name

        filepath = bpy.path.abspath(collection.library.filepath)

        
        if self.save:
            bpy.ops.wm.save_mainfile()

        bpy.ops.wm.open_mainfile(filepath = filepath)

        #linking library back
        target_col = bpy.data.collections.get(collection_name)
        master_col = bpy.context.scene.collection
        
        if target_col and target_col.name not in master_col.children:
            master_col.children.link(target_col)
        return {'FINISHED'}