import bpy  # type: ignore


def run_isolated(context, func, active_object, selected_objects: list, mode: str | None = None):
    prev_mode = "OBJECT"
    prev_selected = list(context.selected_objects)
    prev_active = context.view_layer.objects.active

    try:
        for obj in context.scene.objects:
            obj.select_set(obj in selected_objects)

        ensure_object_selectable(context, active_object)
        context.view_layer.objects.active = active_object

        prev_mode = active_object.mode
        if mode is not None:
            bpy.ops.object.mode_set(mode=mode)

        return func()

    finally:
        for obj in prev_selected:
            obj.select_set(True)

        if prev_active:
            context.view_layer.objects.active = prev_active
            try:
                bpy.ops.object.mode_set(mode=prev_mode)
            except Exception:
                pass


def ensure_object_selectable(context, obj):
    if not obj:
        return

    try:
        if obj.name not in context.scene.objects:
            context.scene.collection.objects.link(obj)
    except Exception as e:
        print(e)

    try:
        if obj.name not in context.view_layer.objects:
            context.view_layer.objects.link(obj)
    except Exception as e:
        print(e)

    try:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_select = False
    except Exception as e:
        print(e)

    try:
        target_collections = set(obj.users_collection)

        def unhide_layer_collection_branch(layer_collection):
            found = layer_collection.collection in target_collections

            for child in layer_collection.children:
                if unhide_layer_collection_branch(child):
                    found = True

            if found:
                layer_collection.hide_viewport = False
                layer_collection.collection.hide_viewport = False

            return found

        unhide_layer_collection_branch(context.view_layer.layer_collection)

    except Exception as e:
        print(e)