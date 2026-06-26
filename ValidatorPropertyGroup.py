import bpy #type: ignore


class USD_PG_ExportHookSettings(bpy.types.PropertyGroup):

    enable_export_usd_hook: bpy.props.BoolProperty(
        name="Enable Export Hook",
        description="Toggle whether USD export runs automatically after saving the blend file.",
        default=False,
    ) #type: ignore

    export_type: bpy.props.EnumProperty(
        items=[
            ("usda", "usda", "usda"),
            ("usdc", "usdc", "usdc"),

        ],
        default = "usda"
    )#type: ignore

    export_root_directory: bpy.props.StringProperty(
        subtype = 'DIR_PATH',
        default = "X:\\PROD\\_export\\"
    )#type: ignore

    high_poly_collection: bpy.props.PointerProperty(type=bpy.types.Collection) #type: ignore

    usd_asset_type: bpy.props.StringProperty() #type: ignore
