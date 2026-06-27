import bpy #type: ignore
import bmesh #type: ignore
from .fixer_factory import make_fixer
from typing import Callable

class ValidationResult():
    def __init__(self, error_type: str, error_object:str, error_message:str, is_critical:bool, fixer:str | None = None) -> None: 
        self.error_type:str = error_type
        self.error_object:str = error_object
        self.error_message:str = error_message
        self.is_critical:bool = is_critical
        self.fixer: str | None = fixer

def missing_collision(obj) -> list[ValidationResult]:
    from .fixes import fix_missing_collision

    missing_collision_results = []
    
    if obj.type != "MESH":
        return missing_collision_results

    if is_collision_mesh(obj):
        return missing_collision_results

    name = obj.data.name
    for child in obj.children:
        if child.name.startswith(f"UCX_{name}"):
            return missing_collision_results

    _, fixer = make_fixer("fix_collision", fix_missing_collision, {"obj": obj})

    missing_collision_results.append(
        ValidationResult(
            error_type="missing_collision",
            error_object=obj.name,
            error_message=f"{obj.name} is missing collisions",
            is_critical=False,
            fixer = fixer
        )
    )

    print("missing collision: ",len(missing_collision_results))
    return missing_collision_results

def missing_material(obj) -> list[ValidationResult]:
    missing_material_results = []

    if obj.type != "MESH":
        return missing_material_results

    if is_collision_mesh(obj):
        return missing_material_results

    if len(obj.material_slots) == 0:
        missing_material_results.append(
            ValidationResult(
                error_type="missing_material",
                error_object=obj.name,
                error_message=f"{obj.name} doesnt have a material",
                is_critical=False
            )
        )

    print("missing material: ", len(missing_material_results))
    return missing_material_results

def convex_collision(obj) -> list[ValidationResult]:
    convex_collision_results = []

    if not is_collision_mesh(obj):
        return convex_collision_results

    conv = convexity(obj)
    if conv < 0.99:

        from .fixes import fix_convex_collision
        data = {
            "parent": obj.parent,
            "obj": obj
        }
        _, fixer = make_fixer("fix_convexity", fix_convex_collision, data)

        convex_collision_results.append(
            ValidationResult(
                error_type="concave_colliders",
                error_object=obj.name,
                error_message=f"{obj.name} has a convexity of {conv}",
                is_critical=True,
                fixer = fixer
            )
        )

    print("concave collision: ", len(convex_collision_results))
    return convex_collision_results

def wrong_purpose(obj) -> list[ValidationResult]:
    wrong_purpose_results = []
    purpose = obj.get("purpose")

    if is_collision_mesh(obj):
        if purpose not in {"proxy", "collision"}:
            wrong_purpose_results.append(
                ValidationResult(
                    error_type="wrong_purposes",
                    error_object=obj.name,
                    error_message=f"{obj.name} should have proxy or collision purpose",
                    is_critical=True
                )
            )

    else:
        if purpose in {"proxy", "collision"}:
            wrong_purpose_results.append(
                ValidationResult(
                    error_type="wrong_purposes",
                    error_object=obj.name,
                    error_message=f"{obj.name} should not have proxy or collision purpose",
                    is_critical=True
                )
            )

    print("wrong purpose: ", len(wrong_purpose_results))
    return wrong_purpose_results

def wrong_data_names(obj) -> list[ValidationResult]:
    prefixes = {
        "EMPTY": "GRP_",
        "MESH": "GEO_",
        "CURVE": "CRV_",
    }

    wrong_name_results = []
    if is_collision_mesh(obj):
        if has_wrong_collision_name(obj):
            wrong_name_results.append(
                ValidationResult(
                    error_type="wrong_data_names",
                    error_object=obj.name,
                    error_message=f"{obj.name} has wrong collision name",
                    is_critical=True
                )
            )

    else:
        prefix = prefixes.get(obj.type)
        if prefix: 
            result = has_wrong_data_names(obj, prefix)
            wrong_name_results.extend(result)
            
    print("wrong names: ", len(wrong_name_results))
    return wrong_name_results

# helpers

def has_wrong_data_names(obj, prefix_data):
    results = []
    name = obj.name
    if not obj.name.startswith(prefix_data):
        results.append( 
            ValidationResult(
                    error_type="wrong_data_names",
                    error_object=obj.name,
                    error_message=f"Object name doesnt start with {prefix_data}",
                    is_critical=False
                )   
            )
    prefix_removed = name.removeprefix(prefix_data)
    data_name = obj.data.name if obj.data else ""
    false_data_name = data_name != prefix_removed
    if false_data_name:
        results.append( 
            ValidationResult(
                    error_type="wrong_data_names",
                    error_object=obj.name,
                    error_message=f"datablock name and obj name dont match",
                    is_critical=True
                )
            )
    return results

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
        
    return original_volume / hull_volume

def is_collision_mesh(obj):
    name = obj.name.lower()
    if name.startswith(f"ucx_") or name.startswith(f"ubx_") or name.startswith(f"usp_"):
        return True
    return False