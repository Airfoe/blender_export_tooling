import bpy #type: ignore
from rules import missing_collision, missing_material, convex_collision, wrong_data_name, wrong_purpose

def scene_validator(context):
    settings = context.scene.usd_validator_settings
    cache = settings.cache

    cache.missing_collision.clear()
    cache.missing_material.clear()
    cache.concave_colliders.clear()
    cache.wrong_purposes.clear()
    cache.wrong_data_names.clear()
    scene_valid = True

    results = []
    for obj in bpy.data.objects:

        if is_excluded(obj):
            continue

        results.append(missing_collision(obj))
        results.append(missing_material(obj))
        results.append(convex_collision(obj))
        results.append(wrong_data_name(obj))
        results.append(wrong_purpose(obj))

    for result in results:
        item = cache.get(result.error_type).add()
        item.type = result.error_type
        item.object_name = result.error_object
        item.message = result.error_message
        item.is_critical = result.is_critical

def is_excluded(obj):
    if not obj:
        return True

    if obj.library:
        return True

    if obj.data and obj.data.library:
        return True