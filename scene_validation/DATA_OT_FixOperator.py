import bpy #type: ignore
from ..constants import get_operator
from typing import Callable

class DATA_OT_FixOperator(bpy.types.Operator):
    bl_idname = get_operator('FixOperator')
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    fixer: Callable

    def execute(self, context):

        #run fixer function

        return {'FINISHED'}