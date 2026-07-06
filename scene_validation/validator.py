from pathlib import Path
import bpy  # type: ignore
from .core import RULES, ERROR
from . import rules, fixes


def validate_scene(context) -> list:
    """Run all rules over the export collection, store the results in the cache and return them."""
    cache = context.scene.usd_validator_settings.cache
    cache.issues.clear()

    issues = []
    for obj in get_export_objects():
        if is_excluded(obj):
            continue
        for rule in RULES:
            issues.extend(rule(obj))

    for issue in issues:
        item = cache.issues.add()
        item.category = issue.category
        item.object_name = issue.object_name
        item.message = issue.message
        item.severity = issue.severity
        item.fix_id = issue.fix_id

    return issues


def get_export_objects():
    """Only the export collection gets exported, so only validate its objects
    (including nested collections). Falls back to everything when there is
    no export collection to look at yet."""
    collection = get_export_collection()
    if collection is None:
        return bpy.data.objects
    return collection.all_objects


def get_export_collection():
    # the exporter exports the collection named like the blend file (see OBJECT_OT_ExportUSD)
    if not bpy.data.filepath:
        return None
    return bpy.data.collections.get(Path(bpy.data.filepath).stem)


def has_critical_issues(issues) -> bool:
    return any(issue.severity == ERROR for issue in issues)


def is_excluded(obj) -> bool:
    # linked library objects cant be edited here, so dont validate them
    if obj.library:
        return True
    if obj.data is not None and obj.data.library:
        return True
    return False
