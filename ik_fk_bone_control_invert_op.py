import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_IKFKBControlInvert(bpy.types.Operator):
    bl_idname = "rigpp.ik_fk_bone_control_invert"
    bl_label = "Invert IK FK Chain control"
    bl_description = "Invert IK FK chain control to (flip what is active at position 0)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.mode != "POSE":
            return False

        return not (not findCreatedChains(context))

    def execute(self, context):
        count = 0
        chains=findCreatedChains(context)
        for chain in chains:
            
            obj = chain.obj
            bones = obj.pose.bones
            
            for bone in chain.deform():
                pBone = bones[bone]
                
                for d in obj.animation_data.drivers:
                    bonePath = 'pose.bones["'+pBone.name+'"].constraints'
                    dp = d.data_path
                    if not dp.startswith(bonePath):
                        continue
                    
                    if not any(#none
                            bonePath+'["'+c.name+'"].influence' == dp and
                            c.type == "COPY_TRANSFORMS"
                            for c in pBone.constraints):
                        continue
                    
                    d = d.driver
                    
                    dp = d.variables[0].targets[0].data_path
                    
                    if dp.startswith('["') and dp.endswith('"]'):
                        dp = dp[2: -2]
                    else:
                        continue
                    
                    if dp != chain.name:
                        continue
                    
                    count += 1
                    
                    invertSingleVariableDriver(d)

        if count > 0:
            cLen=len(chains)
            self.report({'INFO'}, 
            "Flipped "+str(count) +" IK FK bone influence"+s(count)+" in "
            +str(cLen)+" chain"+s(cLen)+"!")

        return {"FINISHED"}
