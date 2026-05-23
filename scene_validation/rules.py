import bpy #type: ignore
import bmesh #type: ignore

from typing import Callable

class ValidationResult():
    def __init__(self, error_type: str, error_object:str, error_message:str, is_critical:bool) -> None: 
        self.error_type:str = error_type
        self.error_object:str = error_object
        self.error_message:str = error_message
        self.is_critical:bool = is_critical

def missing_collision(obj) -> list[ValidationResult]:
    results = []
    name = obj.name.lower()
    
    if obj.type != "MESH":
        return results

    if is_collision_mesh(obj):
        return results

    for child in obj.children:
        if child.name.lower().startswith(f"ucx_{name}"):
            return results

    results.append(
        ValidationResult(
            error_type="missing_collision",
            error_object=obj.name,
            error_message=f"{obj.name} is missing collisions",
            is_critical=False
        )
    )

    return results

def missing_material(obj) -> list[ValidationResult]:
    results = []

    if obj.type != "MESH":
        return results

    if is_collision_mesh(obj):
        return results

    if len(obj.material_slots) == 0:
        results.append(
            ValidationResult(
                error_type="missing_material",
                error_object=obj.name,
                error_message=f"{obj.name} doesnt have a material",
                is_critical=False
            )
        )

    return results

def convex_collision(obj) -> list[ValidationResult]:
    results = []

    if not is_collision_mesh(obj):
        return results

    conv = convexity(obj)
    if conv < 0.99:

        results.append(
            ValidationResult(
                error_type="concave_collision",
                error_object=obj.name,
                error_message=f"{obj.name} has a convexity of {conv}",
                is_critical=True
            )
        )

    return results

def wrong_purpose(obj) -> list[ValidationResult]:
    results = []
    purpose = obj.get("purpose")

    if is_collision_mesh(obj):
        if purpose not in {"proxy", "collision"}:
            results.append(
                ValidationResult(
                    error_type="wrong_purpose",
                    error_object=obj.name,
                    error_message=f"collision obj {obj.name} should have proxy or collision purpose",
                    is_critical=True
                )
            )

    else:
        if purpose in {"proxy", "collision"}:
            results.append(
                ValidationResult(
                    error_type="wrong_purpose",
                    error_object=obj.name,
                    error_message=f"regular obj {obj.name} should not have proxy or collision purpose",
                    is_critical=True
                )
            )

    return results

def wrong_data_name(obj) -> list[ValidationResult]:
    prefixes = {
        "EMPTY": "GRP_",
        "MESH": "GEO_",
        "CURVE": "CRV_",
    }

    results = []
    if is_collision_mesh(obj):
        if has_wrong_collision_name(obj):
            results.append(
                ValidationResult(
                    error_type="wrong_data_name",
                    error_object=obj.data.name,
                    error_message="wrong collision name",
                    is_critical=True
                )
            )

    else:
        prefix = prefixes.get(obj.type)
        if prefix and has_wrong_obj_name(obj, prefix):
            results.append(
                ValidationResult(
                    error_type="wrong_data_name",
                    error_object=obj.name,
                    error_message=f"should have {prefix} as prefix",
                    is_critical=False
                )
            )

    return results

# helpers

def has_wrong_obj_name(obj, prefix_data):
    name = obj.name
    if name.endswith("_inst"):
        return None

    prefix_removed = name.removeprefix(prefix_data)
    data_name = obj.data.name if obj.data else ""
    false_geo_name = data_name != prefix_removed
    return false_geo_name

def has_wrong_collision_name(obj):
    raw_name = obj.name.removeprefix("UCX_")
    if not obj.parent.data.name.startswith(raw_name):
        return None
    return None

def convexity(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    
    original_volume = abs(bm.calc_volume())
    hull_bm = bm.copy()

    bmesh.ops.delete(
        hull_bm, 
        geom=hull_bm.faces[:] + hull_bm.edges[:], 
        context='FACES_ONLY'
    )

    bmesh.ops.convex_hull(
        hull_bm,
        input=hull_bm.verts
    )

    hull_bm.normal_update()
    hull_volume = abs(hull_bm.calc_volume())

    bm.free()
    hull_bm.free()

    # womp womp, stopid calculator cant divide by 0
    if hull_volume == 0:
        return 0
        
    print(original_volume / hull_volume)
    return original_volume / hull_volume

def is_collision_mesh(obj):
    name = obj.name.lower()
    if name.startswith(f"ucx_") or name.startswith(f"ubx_") or name.startswith(f"usp_"):
        return True
    return False