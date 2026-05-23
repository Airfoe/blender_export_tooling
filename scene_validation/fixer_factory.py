import bpy #type: ignore

REGISTERED_OPERATORS = []


def make_fixer(name, func, data:dict):
    op = new_operator(name, func, data)
    register_operator(op)
    return op, op.bl_idname

def new_operator(name, func, data:dict):

    passed_data = data

    class DynamicOperator(bpy.types.Operator):
        bl_idname = f"airfoe_fixer.{name}"
        bl_label = name

        def execute(self, context):
            func(context, passed_data)
            return {'FINISHED'}
        
    return DynamicOperator

def register_operator(cls):
    bpy.utils.register_class(cls)
    REGISTERED_OPERATORS.append(cls)