import bpy #type: ignore

import bpy  # type: ignore


class USD_PG_ValidationItem(bpy.types.PropertyGroup):
    type: bpy.props.StringProperty() #type: ignore
    message: bpy.props.StringProperty() #type: ignore
    object_name: bpy.props.StringProperty() #type: ignore
    expected: bpy.props.StringProperty() #type: ignore
    found: bpy.props.StringProperty() #type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    fix_operator: bpy.props.StringProperty() #type: ignore
    fix_object_name: bpy.props.StringProperty() #type: ignore
    fix_data: bpy.props.StringProperty() #type: ignore

class USD_PG_ValidatorCache(bpy.types.PropertyGroup):

    missing_collision: bpy.props.CollectionProperty(type=USD_PG_ValidationItem) #type: ignore
    missing_material: bpy.props.CollectionProperty(type=USD_PG_ValidationItem) #type: ignore
    concave_colliders: bpy.props.CollectionProperty(type=USD_PG_ValidationItem)#type: ignore
    wrong_purposes: bpy.props.CollectionProperty(type=USD_PG_ValidationItem)#type: ignore
    wrong_data_names: bpy.props.CollectionProperty(type=USD_PG_ValidationItem)#type: ignore

    is_dirty: bpy.props.BoolProperty(default=True)#type: ignore

class USD_PG_ValidatorSettings(bpy.types.PropertyGroup):

    cache: bpy.props.PointerProperty(type=USD_PG_ValidatorCache) #type: ignore
    ShowMissingCollision: bpy.props.BoolProperty(name="Show Missing Collision", default=True) #type: ignore
    ShowMissingMaterial: bpy.props.BoolProperty(name="Show Missing Material", default=True) #type: ignore
    ShowConcaveCollider: bpy.props.BoolProperty(name="Show Concave Collider", default=True) #type: ignore
    ShowWrongPurpose: bpy.props.BoolProperty(name="Show Wrong Purpose", default=True) #type: ignore
    ShowWrongDataName: bpy.props.BoolProperty(name="Show Wrong Data Name", default=True) #type: ignore

    IsDirty: bpy.props.BoolProperty(default=True) #type: ignore


class USD_PG_ExportHookSettings(bpy.types.PropertyGroup):

    enable_export_usd_hook: bpy.props.BoolProperty(
        name="Enable Export Hook",
        description="Toggle whether USD export runs automatically after saving the blend file.",
        default=False,
    ) #type: ignore


    usd_asset_type: bpy.props.StringProperty() #type: ignore
