import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone, PoseBone
from mathutils import Matrix, Vector, Euler
from mathutils.geometry import interpolate_bezier, intersect_point_line
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_ParentToClosestBone(bpy.types.Operator):
    bl_idname = "rigpp.parent_to_closest_bone"
    bl_label = "Parent To Closest Bone"
    bl_description = "Find closes Bone in active armature and parent selected objects to it"
    bl_options = {'REGISTER', 'UNDO'}
    
    limitDeform: BoolProperty(name="Limit to deform", default=True)
    
    @classmethod
    def poll(self, context):

        if context.mode != "OBJECT" and context.mode != "POSE":
            return False

        if len(context.selected_objects) < 2:
            return False

        target = context.active_object
        if target.type != "ARMATURE":
            return False

        if len(getRelevantBones(target, context)) < 1:
            return False

        return True

    def execute(self, context):

        target = context.active_object

        toParent = list(context.selected_objects)

        for obj in toParent:
            if obj == target:
                continue

            obj.select_set(False)

        bones = target.data.bones

        orgSelect = []
        orgAct = target.data.bones.active

        for bone in bones:
            if bone.select:
                bone.select = False
                orgSelect.append(bone)

        for obj in toParent:
            if obj == target:
                continue

            location = obj.location

            closest = 0
            closestDist = 9999999999999

            for i, bone in enumerate(bones):
                if self.limitDeform and not bone.use_deform:
                    continue
                
                p1=target.matrix_world@bone.head_local
                p2=target.matrix_world@bone.tail_local
                
                point=intersect_point_line(location, p1, p2)[0]
                
                d = (location-point).length
                
                if d < closestDist:
                    closestDist = d
                    closest = i
            
            b = bones[closest]
            
            b.select = True
            target.data.bones.active = b

            obj.select_set(True)
            bpy.ops.object.parent_set(type='BONE', keep_transform=True)
            obj.select_set(False)

            b.select = False

        target.data.bones.active = orgAct
        for bone in orgSelect:
            bone.select = True

        for obj in toParent:
            if obj == target:
                continue

            obj.select_set(True)

        return {"FINISHED"}
