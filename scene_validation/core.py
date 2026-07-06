from dataclasses import dataclass

WARNING = "WARNING"
ERROR = "ERROR"


@dataclass
class Issue:
    category: str
    object_name: str
    message: str
    severity: str = WARNING
    fix_id: str = ""


# category id -> how the report dialog displays it.
# the fold-out toggle on USD_PG_ValidatorSettings is named f"show_{category_id}"
CATEGORIES = {
    "missing_collision": {"title": "Objects Missing Collisions", "icon": "MESH_CUBE"},
    "missing_material": {"title": "Objects Missing Materials", "icon": "MATERIAL"},
    "concave_collider": {"title": "Concave Colliders", "icon": "MOD_PHYSICS"},
    "wrong_purpose": {"title": "Wrong Purposes", "icon": "ERROR"},
    "wrong_name": {"title": "Wrong Names", "icon": "SORTALPHA"},
}



RULES = []

def rule(func):
    RULES.append(func)
    return func


FIXERS = {}

def fixer(fix_id):
    def decorator(func):
        FIXERS[fix_id] = func
        return func
    return decorator
