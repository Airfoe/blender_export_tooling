import bpy #type: ignore


class USD_PG_ExportHookSettings(bpy.types.PropertyGroup):

    enable_export_usd_hook: bpy.props.BoolProperty(
        name="Enable Export Hook",
        description="Toggle whether USD export runs automatically after saving the blend file.",
        default=False,
    ) #type: ignore


    usd_asset_type: bpy.props.StringProperty() #type: ignore
