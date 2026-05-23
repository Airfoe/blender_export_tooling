import bpy #type: ignore
from .rules import missing_collision, missing_material, convex_collision, wrong_data_names, wrong_purpose
from typing import Callable


default_rules = [
    missing_collision, 
    missing_material, 
    convex_collision, 
    wrong_data_names, 
    wrong_purpose
    ]

def scene_validator(context, rules: list[Callable] = default_rules):
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

        print(obj.name, obj.data.name)
        for rule in rules:
            results.extend(rule(obj))


    print("overall issues: ", len(results))
    print("-------------------------")
    for result in results:
        print(result.error_type)
        error_collection = getattr(cache, result.error_type, None)
        if error_collection is None:
            print(result.error_type, " could not be added to cache")
            continue

        item = error_collection.add()
        item.type = result.error_type
        item.object_name = result.error_object
        item.message = result.error_message
        item.is_critical = result.is_critical
        scene_valid = False
    return scene_valid

def is_excluded(obj):
    if not obj:
        return True

    if obj.library:
        return True

    if obj.data and obj.data.library:
        return True