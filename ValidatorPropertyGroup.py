import bpy #type: ignore

class ValidatorSettings(bpy.types.PropertyGroup):
    ShowMissingCollisions: bpy.props.BoolProperty(
        name="Show Missing Collisions",
        description="Toggle whether to display objects missing collisions in the validation report.",
        default=False,
    )#type: ignore

    ShowMissingMaterial: bpy.props.BoolProperty(
        name="Show Missing Material",
        description="Toggle whether to display objects missing material in the validation report.",
        default=False,
    )#type: ignore