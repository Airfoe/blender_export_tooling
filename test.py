# tools/generate_classes.py

import ast
from pathlib import Path


ADDON_ROOT = Path(__file__).parent
print(ADDON_ROOT)

OUTPUT_FILE = ADDON_ROOT / "generated_classes.py"


def split_classes(classes):
    operators = []
    panels = []
    property_groups = []
    preferences = []

    for c in classes:
        if "_OT_" in c:
            operators.append(c)

        if "_PT_" in c:
            panels.append(c)

        if "_PG_" in c:
            property_groups.append(c)

        if "Preferences" in c:
            preferences.append(c)
    
    return {
        "operators": operators,
        "panels": panels,
        "property_groups": property_groups,
        "preferences": preferences
    }
    
            
            
            

    pass

def find_classes(py_file: Path):
    """Extract class names from a file via AST (no imports executed)."""

    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))

    classes = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and is_blender_class(node):
            classes.append(node.name)

    return classes


def is_blender_class(node: ast.ClassDef):
    name = node.name

    return any(
        tag in name
        for tag in ("_OT_", "_PT_", "_PG_", "Preferences")
    )

def module_import_path(py_file: Path):
    rel = py_file.relative_to(ADDON_ROOT).with_suffix("")
    return ".".join(rel.parts)


def main():
    imports = []
    class_names = []

    for py_file in ADDON_ROOT.rglob("*.py"):
        if "__init__" in py_file.name:
            continue


        classes = find_classes(py_file)

        if not classes:
            continue

        for cls in classes:
            imports.append(f"from .{module_import_path(py_file)} import {cls}")
            class_names.append(cls)


    output = []

    output.append("# AUTO-GENERATED FILE")
    output.append("")

    sorted_classes = split_classes(class_names)
    output.extend(imports)
    output.append("")
    output.append("CLASSES = (")
    output.append("\n#preferences")
    output.extend(f"{pref}," for pref in sorted_classes["preferences"])
    
    output.append("\n#Property Groups")
    output.extend(f"{pg}," for pg in sorted_classes["property_groups"])
    
    output.append("\n#Operators")
    output.extend(f"{op}," for op in sorted_classes["operators"])
    
    output.append("\n#Panels")
    output.extend(f"{pt}," for pt in sorted_classes["panels"])
    
    output.append(")")
    output.append("")

    OUTPUT_FILE.write_text("\n".join(output))

    print(f"Generated {OUTPUT_FILE}")



if __name__ == "__main__":
    main()