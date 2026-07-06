import bpy  # type: ignore

from ..constants import get_operator
from ..scene_validation.core import CATEGORIES, ERROR
from ..scene_validation.validator import validate_scene
from .OBJECT_OT_SelectObject import OBJECT_OT_SelectObject
from .OBJECT_OT_FixValidationIssue import OBJECT_OT_FixValidationIssue

SEVERITY_ICONS = {
    "ERROR": "CANCEL",
    "WARNING": "ERROR",  # blenders warning triangle
}


class OBJECT_OT_ValidateUSD(bpy.types.Operator):
    bl_idname = get_operator("validate_usd")
    bl_label = "USD Validation Report"
    bl_description = "Validate USD scene"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        validate_scene(context)
        return context.window_manager.invoke_props_dialog(self, width=600)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        cache = context.scene.usd_validator_settings.cache

        header_box = layout.box()
        header_box.label(text="USD Validation Report", icon="INFO")

        for category, info in CATEGORIES.items():
            items = [item for item in cache.issues if item.category == category]
            self.draw_section(context, category, info, items)

    def draw_section(self, context, category, info, items):
        box = self.layout.box()

        if not items:
            box.label(text=f"{info['title']}: 0", icon="CHECKMARK")
            return

        settings = context.scene.usd_validator_settings
        toggle_prop = f"show_{category}"
        is_open = getattr(settings, toggle_prop)
        has_error = any(item.severity == ERROR for item in items)

        # header, highlighted if it hides critical issues
        box.alert = has_error and not is_open
        row = box.row(align=True)
        row.prop(
            settings,
            toggle_prop,
            text="",
            emboss=False,
            icon="DOWNARROW_HLT" if is_open else "RIGHTARROW"
        )
        row.label(text=f"{info['title']}: {len(items)}", icon=info["icon"])

        if not is_open:
            return

        box.alert = False
        content = box.column(align=True)
        for item in items:
            row = content.row(align=True)
            row.alert = item.severity == ERROR
            row.label(
                text=item.message,
                icon=SEVERITY_ICONS.get(item.severity, "QUESTION")
            )

            if item.object_name and item.object_name in bpy.data.objects:
                row.operator(
                    OBJECT_OT_SelectObject.bl_idname,
                    text="",
                    icon="RESTRICT_SELECT_OFF"
                ).object_name = item.object_name

            if item.fix_id:
                op = row.operator(
                    OBJECT_OT_FixValidationIssue.bl_idname,
                    text="",
                    icon="CHECKMARK"
                )
                op.fix_id = item.fix_id
                op.object_name = item.object_name
