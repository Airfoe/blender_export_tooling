import bpy  # type: ignore

from ..helpers.usd_helpers import usd_validator
from ..constants import get_operator
from .OBJECT_OT_SelectObject import OBJECT_OT_SelectObject


class OBJECT_OT_ValidateUSD(bpy.types.Operator):
    bl_idname = get_operator("validate_usd")
    bl_label = "USD Validation Report"
    bl_description = "Validate USD scene"
    bl_options = {"REGISTER", "UNDO"}

    validation_results = None

    def invoke(self, context, event):
        self.validation_results = usd_validator(context)
        return context.window_manager.invoke_props_dialog(
            self,
            width=600
        )

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        header_box = layout.box()
        header_box.label(
            text="USD Validation Report",
            icon="INFO"
        )

        results = self.validation_results

        self.draw_error_section(
            context=context,
            title="Objects Missing Collisions",
            toggle_prop="ShowMissingCollisions",
            items=results.get("missing_collisions", []),
            icon="MESH_CUBE"
        )

        self.draw_error_section(
            context=context,
            title="Objects Missing Materials",
            toggle_prop="ShowMissingMaterial",
            items=results.get("missing_material", []),
            icon="MATERIAL"
        )

        self.draw_error_section(
            context=context,
            title="Hierarchy Errors",
            toggle_prop="ShowHierarchyErrors",
            items=results.get("hierarchy_errors", []),
            icon="OUTLINER_COLLECTION"
        )

    # ---------------------------------------------------------
    # GENERIC ERROR SECTION
    # ---------------------------------------------------------

    def draw_error_section(
        self,
        context,
        title,
        toggle_prop,
        items,
        icon="ERROR"
    ):
        if not items:
            return

        settings = context.scene.usd_validator_settings
        box = self.layout.box()

        # -----------------------------------
        # Header
        # -----------------------------------

        row = box.row(align=True)
        is_open = getattr(settings, toggle_prop)

        row.prop(
            settings,
            toggle_prop,
            text="",
            emboss=False,
            icon="DOWNARROW_HLT" if is_open else "RIGHTARROW"
        )

        row.label(
            text=f"{title}: {len(items)}",
            icon=icon
        )

        # -----------------------------------
        # Expanded Contents
        # -----------------------------------

        if not is_open:
            return
        content = box.column(align=True)

        for item in items:
            row = content.row(align=True)

            # -----------------------------------
            # OBJECT ITEMS
            # -----------------------------------
            if isinstance(item, bpy.types.Object):
                row.label(
                    text=item.name,
                    icon="ERROR"
                )

                row.operator(
                    OBJECT_OT_SelectObject.bl_idname,
                    text="",
                    icon="RESTRICT_SELECT_OFF"
                ).object_name = item.name

            # -----------------------------------
            # DICTIONARY ITEMS
            # -----------------------------------
            elif isinstance(item, dict):
                row.label(
                    text=item.get("message", "Unknown Error"),
                    icon="ERROR"
                )

                obj = item.get("object")
                if obj:
                    row.operator(
                        OBJECT_OT_SelectObject.bl_idname,
                        text="",
                        icon="RESTRICT_SELECT_OFF"
                    ).object_name = obj.name

            # -----------------------------------
            # STRING ITEMS
            # -----------------------------------
            else:
                row.label(
                    text=str(item),
                    icon="ERROR"
                )