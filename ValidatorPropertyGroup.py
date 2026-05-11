import bpy #type: ignore

import bpy  # type: ignore


class USDValidationItem(bpy.types.PropertyGroup):
    type: bpy.props.StringProperty() #type: ignore
    message: bpy.props.StringProperty() #type: ignore
    object_name: bpy.props.StringProperty() #type: ignore
    expected: bpy.props.StringProperty() #type: ignore
    found: bpy.props.StringProperty() #type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    fix_operator: bpy.props.StringProperty() #type: ignore
    fix_object_name: bpy.props.StringProperty() #type: ignore
    fix_data: bpy.props.StringProperty() #type: ignore

class USDValidatorCache(bpy.types.PropertyGroup):

    missing_collision: bpy.props.CollectionProperty(type=USDValidationItem) #type: ignore
    missing_material: bpy.props.CollectionProperty(type=USDValidationItem) #type: ignore
    concave_colliders: bpy.props.CollectionProperty(type=USDValidationItem)#type: ignore
    wrong_purposes: bpy.props.CollectionProperty(type=USDValidationItem)#type: ignore
    wrong_data_names: bpy.props.CollectionProperty(type=USDValidationItem)#type: ignore

    is_dirty: bpy.props.BoolProperty(default=True)#type: ignore

class USDValidatorSettings(bpy.types.PropertyGroup):

    cache: bpy.props.PointerProperty(type=USDValidatorCache) #type: ignore
    ShowMissingCollision: bpy.props.BoolProperty(name="Show Missing Collision", default=True) #type: ignore
    ShowMissingMaterial: bpy.props.BoolProperty(name="Show Missing Material", default=True) #type: ignore
    ShowConcaveCollider: bpy.props.BoolProperty(name="Show Concave Collider", default=True) #type: ignore
    ShowWrongPurpose: bpy.props.BoolProperty(name="Show Wrong Purpose", default=True) #type: ignore
    ShowWrongDataName: bpy.props.BoolProperty(name="Show Wrong Data Name", default=True) #type: ignore

    IsDirty: bpy.props.BoolProperty(default=True) #type: ignore