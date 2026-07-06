import re
import bmesh  # type: ignore
from .core import Issue, rule, WARNING, ERROR

# UE collision prefixes: convex, box, sphere, capsule
COLLISION_PREFIXES = ("UCX_", "UBX_", "USP_", "UCP_")

DATA_PREFIXES = {
    "EMPTY": "GRP_",
    "MESH": "GEO_",
    "CURVE": "CRV_",
}

CONVEXITY_THRESHOLD = 0.99


@rule
def missing_collision(obj) -> list[Issue]:
    if obj.type != "MESH" or is_collision_mesh(obj):
        return []

    if any(is_collision_mesh(child) for child in obj.children):
        return []

    return [Issue(
        category="missing_collision",
        object_name=obj.name,
        message=f"{obj.name} is missing collisions",
        severity=WARNING,
        fix_id="create_collision",
    )]


@rule
def missing_material(obj) -> list[Issue]:
    if obj.type != "MESH" or is_collision_mesh(obj):
        return []

    if len(obj.material_slots) > 0:
        return []

    return [Issue(
        category="missing_material",
        object_name=obj.name,
        message=f"{obj.name} doesnt have a material",
        severity=WARNING,
    )]


@rule
def concave_collider(obj) -> list[Issue]:
    if not is_collision_mesh(obj) or obj.type != "MESH":
        return []

    conv = convexity(obj)
    if conv >= CONVEXITY_THRESHOLD:
        return []

    return [Issue(
        category="concave_collider",
        object_name=obj.name,
        message=f"{obj.name} has a convexity of {conv:.2f}",
        severity=ERROR,
        fix_id="make_convex",
    )]


@rule
def wrong_purpose(obj) -> list[Issue]:
    purpose = obj.get("purpose")

    if is_collision_mesh(obj):
        if purpose not in {"proxy", "collision"}:
            return [Issue(
                category="wrong_purpose",
                object_name=obj.name,
                message=f"{obj.name} should have proxy or collision purpose",
                severity=ERROR,
                fix_id="set_collision_purpose",
            )]

    elif purpose in {"proxy", "collision"}:
        return [Issue(
            category="wrong_purpose",
            object_name=obj.name,
            message=f"{obj.name} should not have proxy or collision purpose",
            severity=ERROR,
            fix_id="clear_purpose",
        )]

    return []


@rule
def wrong_name(obj) -> list[Issue]:
    if is_collision_mesh(obj):
        return collision_name_issues(obj)
    return data_name_issues(obj)


# helpers

def collision_name_issues(obj) -> list[Issue]:
    if obj.parent is None:
        return [Issue(
            category="wrong_name",
            object_name=obj.name,
            message=f"{obj.name} is a collider without a parent",
            severity=ERROR,
        )]

    # UE convention: UCX_<RenderMeshName> with optional _## suffix
    expected = obj.name[:4].upper() + parent_base_name(obj.parent)
    if not re.fullmatch(re.escape(expected) + r"(_\d+)?", obj.name):
        return [Issue(
            category="wrong_name",
            object_name=obj.name,
            message=f"{obj.name} should be named {expected}_##",
            severity=ERROR,
            fix_id="rename_collider",
        )]

    if obj.data and obj.data.name != obj.name:
        return [Issue(
            category="wrong_name",
            object_name=obj.name,
            message=f"{obj.name}: datablock name and object name dont match",
            severity=ERROR,
            fix_id="sync_data_name",
        )]

    return []


def data_name_issues(obj) -> list[Issue]:
    prefix = DATA_PREFIXES.get(obj.type)
    if not prefix:
        return []

    issues = []
    if not obj.name.startswith(prefix):
        issues.append(Issue(
            category="wrong_name",
            object_name=obj.name,
            message=f"{obj.name} doesnt start with {prefix}",
            severity=WARNING,
        ))

    if obj.data and obj.data.name != obj.name.removeprefix(prefix):
        issues.append(Issue(
            category="wrong_name",
            object_name=obj.name,
            message=f"{obj.name}: datablock name and object name dont match",
            severity=ERROR,
            fix_id="sync_data_name",
        ))

    return issues


def parent_base_name(parent):
    return parent.data.name if parent.data else parent.name


def is_collision_mesh(obj) -> bool:
    return obj.name.upper().startswith(COLLISION_PREFIXES)


def convexity(obj) -> float:
    """Volume of the mesh divided by the volume of its convex hull (1.0 = fully convex)."""
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
    bmesh.ops.convex_hull(hull_bm, input=hull_bm.verts)
    hull_bm.normal_update()
    hull_volume = abs(hull_bm.calc_volume())

    bm.free()
    hull_bm.free()

    if hull_volume == 0:
        return 0
    return original_volume / hull_volume
