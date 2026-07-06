import bpy  # type: ignore

from ..constants import get_operator
from ..scene_validation.core import FIXERS
from ..scene_validation.validator import validate_scene


class OBJECT_OT_FixValidationIssue(bpy.types.Operator):
    bl_idname = get_operator("fix_validation_issue")
    bl_label = "Fix Issue"
    bl_description = "Apply the automatic fix for this validation issue"
    bl_options = {"REGISTER", "UNDO"}

    fix_id: bpy.props.StringProperty() #type: ignore
    object_name: bpy.props.StringProperty() #type: ignore

    def execute(self, context):
        fix = FIXERS.get(self.fix_id)
        if fix is None:
            self.report({"ERROR"}, f"Unknown fix: {self.fix_id}")
            return {"CANCELLED"}

        obj = bpy.data.objects.get(self.object_name)
        if obj is None:
            self.report({"ERROR"}, f"Object not found: {self.object_name}")
            return {"CANCELLED"}

        fix(context, obj)

        # rerun validation so the report dialog shows the updated state
        validate_scene(context)
        return {"FINISHED"}
