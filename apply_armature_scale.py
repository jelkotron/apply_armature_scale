bl_info = {
    "name": "Apply Armature Scale",
    "author": "Oliver Jelko",
    "version": (0, 1),
    "blender": (4, 0, 1),
    "location": "View3D > Object > Apply > Apply Scale to Animated Armature",
    "description": "Applies scale of animated armature considering it's animation",
    "warning": "",
    "doc_url": "",
    "category": "Apply Transform",
}

import bpy
import mathutils
       
class AnimatedScaleApply(bpy.types.Operator):
    """Apply scale to animated armature adjusting translation data"""
    bl_idname = "object.animated_scale_apply"
    bl_label = "Apply Scale to Animated Armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        apply_fcurve_scale(bpy.context.active_object)
        return {'FINISHED'}
       
def apply_scale(object):
    matrix_transform = object.matrix_world.copy()
    translation, rotation, scale = matrix_transform.decompose()
    # apply scale, tmp reset translation & rotation
    object.data.transform(mathutils.Matrix.LocRotScale(None, None, scale)) 
    object.matrix_world.identity()
    # restore translation & rotation
    object.matrix_world = mathutils.Matrix.LocRotScale(translation, rotation, None)
    object.data.bones.update()
        
def apply_fcurve_scale(armature):
    if armature.type == 'ARMATURE':
        action = armature.animation_data.action
        scale = armature.scale.copy()
        location_curves = []
        apply_scale(armature)
        
        for fcurve in action.fcurves:
            if fcurve.data_path.endswith("location"):
                location_curves.append(fcurve)
        
        for i in range(len(location_curves)):
            fcurve = location_curves[i]
            for point in fcurve.keyframe_points:
                # account for x,y,z scale
                inverse_scale_factor = 1 / scale[i % len(scale)]
                point.co[1] /= inverse_scale_factor
    else:
        print("Error: Only Armature objects supported yet.")

def menu_func(self, context):
    self.layout.operator(AnimatedScaleApply.bl_idname)

# Register and add to the apply transform menu
def register():
    bpy.utils.register_class(AnimatedScaleApply)
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)

def unregister():
    bpy.utils.unregister_class(AnimatedScaleApply)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()