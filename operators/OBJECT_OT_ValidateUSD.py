import bpy  # type: ignore

from ..scene_validation.validator import scene_validator
from ..constants import get_operator
from .OBJECT_OT_SelectObject import OBJECT_OT_SelectObject


class OBJECT_OT_ValidateUSD(bpy.types.Operator):
    bl_idname = get_operator("validate_usd")
    bl_label = "USD Validation Report"
    bl_description = "Validate USD scene"
    bl_options = {"REGISTER", "UNDO"}

    validation_results = None

    def invoke(self, context, event):
        self.validation_results = scene_validator(context)
        return context.window_manager.invoke_props_dialog(
            self,
            width=600
        )

    def execute(self, context):
        # remove dynamic operators
        from ..scene_validation.fixer_factory import REGISTERED_OPERATORS
        for operator in REGISTERED_OPERATORS:
            try:
                bpy.utils.unregister_class(operator)
            except Exception as e:
                print(e)
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

        self.draw_error_section(
            context=context,
            title="Wrong Data Names",
            toggle_prop="ShowWrongDataName",
            items=cache.wrong_data_names,
            icon="INFO"
        )

    def draw_error_section(self,context,title,toggle_prop,items,icon="ERROR"):
        if not items:
            box = self.layout.box()
            row = box.row()
            row.label(
            text=f"{title}: {len(items)}",
            icon="CHECKMARK"
            )
            return
        

        settings = context.scene.usd_validator_settings
        box = self.layout.box()


        # -----------------------------------
        # Header
        # -----------------------------------

        is_open = getattr(settings, toggle_prop)

        
        for item in items:
            if item.level == "ERROR" and not is_open:
                box.alert = True

        row = box.row(align=True)
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
            if item.level == "ERROR":
                content.alert = True

            # -----------------------------------
            # MESSAGE + SEVERITY
            # -----------------------------------

            icon_enum = {
                "INFO": "INFO",
                "ERROR": "CANCEL",
                "WARNING": "DISCLOSURE_TRI_RIGHT"
            }

            row = content.row(align=True)
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
                        text="",
                        icon="RESTRICT_SELECT_OFF"
                    ).object_name = obj.name

            # -----------------------------------
            # FIX BUTTON
            # -----------------------------------

            if item.fix_operator:
                op = row.operator(
                    item.fix_operator,
                    text="",
                    icon="CHECKMARK"
                )
                if item.fix_object_name:
                    setattr(op, "object_name", item.fix_object_name)

                if item.fix_data:
                    setattr(op, "fix_data", item.fix_data)