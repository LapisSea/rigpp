import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone, EditBone, PoseBone
from mathutils import Matrix, Vector, Euler
from mathutils.geometry import intersect_point_line
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_IKFKBControl(bpy.types.Operator):
    bl_idname = "rigpp.ik_fk_bone_control"
    bl_label = "Bone control IK FK chain"
    bl_description = "Create bone control for an IK FK Chain instead of modinfying custom property in armature datablock"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.mode!="EDIT_ARMATURE":
            return False
        
        for chain in findCreatedChains(context):
            obj = chain.obj
            bones = obj.data.edit_bones
            for fc in obj.animation_data.drivers:
                p=fc.data_path
                if p.startswith('["') and p.endswith('"]') and p[2:-2]==chain.name:
                    return False
            
            return True
            
        return False

    def execute(self, context):
        count = 0
        
        ctrlBones=[]
        
        for chain in findCreatedChains(context):
            
            count += 1
            obj = chain.obj
            bones = obj.data.edit_bones

            posCount = 0
            sum = Vector((0, 0, 0))
            
            startBone=bones[chain.deform()[0]]
            endBone=bones[chain.deform()[-1]]
            
            start = startBone.head
            end = endBone.tail

            args = None

            for name in chain.deform():
                bone: EditBone = bones[name]

                pos = bone.head

                sum += pos
                posCount += 1
                intersect = intersect_point_line(pos, start, end)[0]
                l = (intersect-pos).length
                if args is None or args[2] < l:
                    args = (intersect, pos, l)

                pos = bone.tail

                sum += pos
                posCount += 1
                intersect = intersect_point_line(pos, start, end)[0]
                l = (intersect-pos).length
                if args is None or args[2] < l:
                    args = (intersect, pos, l)

            mid = sum/posCount
            intersect = intersect_point_line(mid, start, end)[0]
            diff = (args[1]-args[0])
            diff /= diff.length


            # midDif = start-mid
            wholeDiff=start-end
            
            
            l = wholeDiff.length
            
            pos = Vector((diff.x*l, diff.y*l, diff.z*l))+intersect
            
            # normal=wholeDiff.copy()
            # normal.normalize()
            
            # tangen=diff.copy()
            # tangen.normalize()
            
            # binorm=tangen.cross(normal)
            # binorm.normalize()
            
            # mat=Matrix((tangen,binorm,normal))
            
            
            name=makeName(chain.name,"ctrl")
            ctrl:EditBone=bones.new(name)
            ctrl.layers=boneLayerWhitelist(4)
            
            name=makeName(chain.name,"ctrl.p")
            ctrlHolder:EditBone=bones.new(name)
            ctrlHolder.layers=boneLayerWhitelist(4)
            
            ctrl.head=pos
            ctrl.tail=pos+Vector((0,0,1))
            ctrl.use_deform = False
            ctrlHolder.head=ctrl.head
            ctrlHolder.tail=ctrl.tail
            ctrlHolder.use_deform = False
            
            ctrl.parent=ctrlHolder
            ctrlHolder.parent=startBone.parent
            
            ctrlBones.append((obj,chain.name,ctrl,ctrlHolder))
        
        
        bpy.ops.object.mode_set(mode='POSE')
        
        groups=standardBoneGroups(obj)
        
        for args in ctrlBones:
            obj,chainName,ctrl,ctrlHolder=args
            ctrl=obj.pose.bones[ctrl.name]
            ctrlHolder=obj.pose.bones[ctrlHolder.name]
            
            constraints=ctrl.constraints
            onlyMove(ctrl,[True,False,True])
            groups.ctrl(ctrl)
            groups.ctrlP(ctrlHolder)
            
            ctrl.custom_shape=getCtrlShape()
            ctrlHolder.custom_shape=getCtrlPShape()
            
            while not(not constraints):
                constraints.remove(constraints[-1])
            
            limit=constraints.new("LIMIT_LOCATION")
            
            limit.owner_space="LOCAL"
            limit.use_transform_limit=True
            limit.use_min_x=True
            limit.use_max_x=True
            limit.use_min_y=True
            limit.use_max_y=True
            limit.use_min_z=True
            limit.use_max_z=True
            limit.max_y=1
            
            driv = obj.driver_add('["'+chainName+'"]').driver
            driv.type = "AVERAGE"
            
            v = driv.variables.new()
            v.name = "value"
            v.type = "TRANSFORMS"
            
            t = v.targets[0]
            t.id = obj
            t.bone_target = ctrl.name
            t.transform_space="LOCAL_SPACE"
            t.transform_type="LOC_Y"
            
            
            
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if count > 0:
            self.report({'INFO'}, "Created "+str(count) +
                        " IK FK chain control bones"+s(count)+"!")

        return {"FINISHED"}
