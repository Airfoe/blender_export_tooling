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
        print(self.validation_results)
        return context.window_manager.invoke_props_dialog(
            self,
            width=600
        )

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.usd_validator_settings
        cache = settings.cache
        header_box = layout.box()
        header_box.label(
            text="USD Validation Report",
            icon="INFO"
        )

        # ---------------------------------------
        # SECTIONS
        # ---------------------------------------

        self.draw_error_section(
            context=context,
            title="Objects Missing Collisions",
            toggle_prop="ShowMissingCollision",
            items=cache.missing_collision,
            icon="MESH_CUBE"
        )

        self.draw_error_section(
            context=context,
            title="Objects Missing Materials",
            toggle_prop="ShowMissingMaterial",
            items=cache.missing_material,
            icon="MATERIAL"
        )

        self.draw_error_section(
            context=context,
            title="Concave Colliders",
            toggle_prop="ShowConcaveCollider",
            items=cache.concave_colliders,
            icon="MOD_PHYSICS"
        )

        self.draw_error_section(
            context=context,
            title="Wrong Purposes",
            toggle_prop="ShowWrongPurpose",
            items=cache.wrong_purposes,
            icon="ERROR"
        )

    def draw_error_section(self,context,title,toggle_prop,items,icon="ERROR"):
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


        if not is_open:
            return
        content = box.column(align=True)

        for item in items:
            row = content.row(align=True)

            # -----------------------------------
            # MESSAGE + SEVERITY
            # -----------------------------------

            icon_enum = {
                "INFO": "INFO",
                "ERROR": "CANCEL",
                "WARNING": "ERROR"
            }

            row.label(
                text=item.message,
                icon=icon_enum.get(item.level, "ERROR")
            )

            # -----------------------------------
            # SELECT OBJECT
            # -----------------------------------
            if item.object_name:
                obj = bpy.data.objects.get(item.object_name)
                if obj:
                    row.operator(
                        OBJECT_OT_SelectObject.bl_idname,
                        text="Select",
                        icon="RESTRICT_SELECT_OFF"
                    ).object_name = obj.name

            # -----------------------------------
            # FIX BUTTON
            # -----------------------------------

            if item.fix_operator:
                op = row.operator(
                    item.fix_operator,
                    text="Fix",
                    icon="CHECKMARK"
                )
                if item.fix_object_name:
                    setattr(op, "object_name", item.fix_object_name)

                if item.fix_new_purpose:
                    setattr(op, "new_purpose", item.fix_new_purpose)