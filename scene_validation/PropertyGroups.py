import bpy  # type: ignore


class USD_PG_ValidationIssue(bpy.types.PropertyGroup):
    category: bpy.props.StringProperty() #type: ignore
    object_name: bpy.props.StringProperty() #type: ignore
    message: bpy.props.StringProperty() #type: ignore
    severity: bpy.props.StringProperty() #type: ignore
    fix_id: bpy.props.StringProperty() #type: ignore


class USD_PG_ValidatorCache(bpy.types.PropertyGroup):
    issues: bpy.props.CollectionProperty(type=USD_PG_ValidationIssue) #type: ignore


class USD_PG_ValidatorSettings(bpy.types.PropertyGroup):
    cache: bpy.props.PointerProperty(type=USD_PG_ValidatorCache) #type: ignore

    # fold-out state per category, named show_<category id> (see core.CATEGORIES)
    show_missing_collision: bpy.props.BoolProperty(default=True) #type: ignore
    show_missing_material: bpy.props.BoolProperty(default=True) #type: ignore
    show_concave_collider: bpy.props.BoolProperty(default=True) #type: ignore
    show_wrong_purpose: bpy.props.BoolProperty(default=True) #type: ignore
    show_wrong_name: bpy.props.BoolProperty(default=True) #type: ignore
