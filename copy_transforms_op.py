import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone, PoseBone
from mathutils import Matrix, Vector, Euler
from mathutils.geometry import interpolate_bezier
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_Copy_Transforms(bpy.types.Operator):
    bl_idname = "rigpp.copy_transforms"
    bl_label = "Copy Transforms"
    bl_description = "Adds copy transforms modifier to selected bones from active"
    bl_options = {'REGISTER', 'UNDO'}
    
    spaces=[
        ("WORLD", "World", "World space"),
        ("LOCAL", "Local", "Local space"),
    ]
    
    fromSpace: EnumProperty(name="From",
                          default="WORLD",
                          items=spaces)
    toSpace: EnumProperty(name="To",
                          default="WORLD",
                          items=spaces)
    
    @classmethod
    def poll(self, context):

        if context.mode != "POSE":
            return False

        target = context.active_object
        if target.type != "ARMATURE":
            return False
            
        if context.active_bone is None:
            return False
        
        if len(context.selected_pose_bones)<2:
            return False
        
        return True

    def execute(self, context):
        target=context.active_bone
        
        for obj in context.objects_in_mode:
            for pBone in obj.pose.bones:
                if pBone.bone==target:
                    continue
                
                if not pBone.bone.select:
                    continue
            
                
                c=pBone.constraints.new("COPY_TRANSFORMS")
                
                c.target=context.active_object
                c.subtarget=target.name
                c.owner_space=self.fromSpace
                c.target_space=self.toSpace
        
        return {"FINISHED"}
