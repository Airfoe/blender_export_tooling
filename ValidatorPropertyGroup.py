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

    parent_class: bpy.props.EnumProperty(
        items = [
            ("actor", "actor", "Default Actor - no exted functionality"),
            ("BP_ItemContainer", "BP_ItemContainer", "Marks Asset as Item Container"),
            ("BP_IngredientProcessor", "BP_IngredientProcessor", "Marks Asset as Ingredient Processor"),
            ("BP_Ingredient", "BP_Ingredient", "Marks Asset as Ingredient"),
            ("BP_RecipeLauncher", "BP_RecipeLauncher", "Catapult"),
            ("BP_CraftingStation", "BP_CraftingStation", "Marks Asset as Crafting Station"),
            ("BP_CraftingButton", "BP_CraftingButton", "Marks Asset as Crafting Button"),
            ("BP_CustomerServing", "BP_CustomerServing", "Marks Asset as Customer Serving"),
            ("BP_GarbageBin", "BP_GarbageBin", "Marks Asset as Garbage Bin"),

        ],
        default = "actor"
        )#type: ignore

    export_root_directory: bpy.props.StringProperty(
        subtype = 'DIR_PATH',
        default = "X:\\PROD\\_export\\"
    )#type: ignore

    high_poly_collection: bpy.props.PointerProperty(type=bpy.types.Collection) #type: ignore

    map_geo_collection: bpy.props.PointerProperty(type=bpy.types.Collection) #type: ignore
    map_asset_collection: bpy.props.PointerProperty(type=bpy.types.Collection) #type: ignore

    export_stage: bpy.props.StringProperty() #type: ignore 

    usd_asset_type: bpy.props.StringProperty() #type: ignore
