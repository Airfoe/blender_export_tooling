import bpy #type: ignore
from ..constants import get_operator
import os
from pathlib import Path
import textwrap


class FILE_OT_MakeAsset(bpy.types.Operator):
    bl_idname = get_operator('MakeAsset')
    bl_label = "Make Asset"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty() #type: ignore

    def invoke(self, context, event):
        if context.active_object:
            self.name = context.active_object.name.removeprefix("GEO_")
        else:
            self.name = "Asset"
        return context.window_manager.invoke_props_dialog(self)

    def get_target_dir(self, context):
        filepath = Path(bpy.data.filepath)
        source = self.find_parent(filepath, "3D")
        target_dir = os.path.join(str(source), "Props", self.name, "src", f"{self.name}.blend")
        return target_dir


    #copied from the internet - i got no clue whats happening but it works
    def find_parent(self, path: Path, folder_name: str) -> Path | None:
        for candidate in [path] + list(path.parents):
            if candidate.name == folder_name:
                return candidate
        return None

    def draw(self, context):
        self.filepath = self.get_target_dir(context)

        layout = self.layout
        layout.prop(self, "name", text="Name")
        
        box = layout.box()
        box.label(text="Included Objects:")
        column = box.column(align=True)
        column.enabled = False
        for obj in context.selected_objects:
            column.label(text=obj.name, icon="OBJECT_DATAMODE")

        wrap_width = 50

        for line in textwrap.wrap(self.filepath, width=wrap_width):
            layout.label(text=line)

    def execute(self, context):
        old_transform = self.move_objects(context)
        collection_instance = self.save_collection_to_path(context)
        if collection_instance and old_transform:
            self.move_collection_back(collection=collection_instance, old_transform=old_transform)
        return {'FINISHED'}

    def move_collection_back(self, collection, old_transform):
        if not old_transform:
            return
        collection.location = old_transform.get("location")
        collection.rotation_euler = old_transform.get("rotation_euler")
        collection.scale = old_transform.get("scale")
        print(f"moved {collection.name} to {old_transform}")

    def move_objects(self, context):
        objects_to_move = context.selected_objects
        if not objects_to_move:
            return None

        pivot_location = (0.0, 0.0, 0.0)
        pivot_rotation = (0.0, 0.0, 0.0)
        pivot_scale =    (1.0, 1.0, 1.0)
        
        pivot_location = context.active_object.location.copy()
        pivot_rotation = context.active_object.rotation_euler.copy()
        pivot_scale = context.active_object.scale.copy()

        temp_parent = bpy.data.objects.new("Temp_Asset_Parent", None)
        context.collection.objects.link(temp_parent)
        temp_parent.location = pivot_location
        temp_parent.rotation_euler = pivot_rotation
        temp_parent.scale = pivot_scale


        # if its stupid and it works its not stupid or something like that~
        for obj in objects_to_move:
            if obj is context.active_object:
                pass
            else:
                obj_matrix_world = obj.matrix_world.copy()
                obj.parent = context.active_object
                obj.matrix_world = obj_matrix_world

        context.active_object.parent = temp_parent
        context.active_object.location = (0,0,0)
        context.active_object.rotation_euler = (0,0,0)

        transform_snapshot = {
            "location": temp_parent.location.copy(),
            "rotation_euler": temp_parent.rotation_euler.copy(),
            "scale": temp_parent.scale.copy()
        }

        temp_parent.location = (0.0, 0.0, 0.0)
        temp_parent.rotation_euler = (0.0, 0.0, 0.0)
        temp_parent.scale = (1.0, 1.0, 1.0)


        # more silly ops thingies
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects_to_move:
            obj.select_set(True)
        context.view_layer.objects.active = objects_to_move[0]
        
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.data.objects.remove(temp_parent, do_unlink=True) #YEEET
        #why am i spamming comments? Idk, its 4am and im tired

        return transform_snapshot

    def save_collection_to_path(self, context):  
        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "Nothing selected!")
            return None
            
        asset_col_name = self.name
        asset_collection = bpy.data.collections.new(asset_col_name)
        context.scene.collection.children.link(asset_collection)
        
        for obj in selected_objects:
            if obj.name not in asset_collection.objects:
                asset_collection.objects.link(obj)
            if obj.name in context.collection.objects:
                context.collection.objects.unlink(obj)

        data_to_write = {asset_collection} | set(selected_objects)
        
        asset_collection.asset_mark()
        asset_collection.asset_data.catalog_id = "919b878c-dcf2-44ec-9764-cb78f4c3f2d3"          # uuid is defined in X:\PROD\3D\blender_asset.cats.txt

        os.makedirs(self.filepath, exist_ok=True)
        bpy.data.libraries.write(self.filepath, data_to_write, fake_user=True)
        
        for obj in selected_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(asset_collection)
            
        with bpy.data.libraries.load(self.filepath, link=True) as (data_from, data_to):
            data_to.collections = [name for name in data_from.collections if name == asset_col_name]
            
        linked_collection = data_to.collections[0]
        if linked_collection is not None:
            instance_object = bpy.data.objects.new(name=asset_col_name, object_data=None)
            instance_object.instance_type = 'COLLECTION'
            instance_object.instance_collection = linked_collection
            context.collection.objects.link(instance_object)
            
            self.report({'INFO'}, f"Wrote asset {self.name} to {self.filepath}")
            return instance_object
        return None