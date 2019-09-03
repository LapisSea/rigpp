import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_IKFKChain(bpy.types.Operator):
    bl_idname = "rigpp.create_ik_fk_chain"
    bl_label = "Create IK FK Chain"
    bl_description = "Create an IK FK chain controls mexed by drivers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.mode != "EDIT_ARMATURE":
            return False
        
        def hasNonCreatedChains(obj):
            bones = obj.data.edit_bones
            
            def isValidChain(chain):
                for bone in chain:
                    if makeName(bone.name,"IK") in bones or makeName(bone.name,"FK") in bones:
                        return False
                return True
            
            return any(isValidChain(b) for b in findChains(bones))
        
        return any(hasNonCreatedChains(o) for o in getArmatures(context))

    def execute(self, context):

        for obj in getArmatures(context):

            armature: Armature = obj.data
            bones = armature.edit_bones
            
            groups=[]
            
            for chain in findChains(bones):
                bpy.ops.object.mode_set(mode='EDIT')

                fk = []
                ik = []

                def makeName(name, addon):

                    segments = name.split(".")
                    insertPos=len(segments)-1
                    
                    if insertPos>0 and isGenNumber(segments[insertPos]):
                        insertPos-=1
                    if  insertPos>0 and isDirection(segments[insertPos]):
                        insertPos-=1
                    
                    segments.insert(insertPos+1,addon)

                    return ".".join(segments)
                
                def newBone(bone, addon, target, layers):
                    name = makeName(bone.name, addon)

                    if name in bones:
                        return True

                    b = bones.new(name)
                    b.head = bone.head
                    b.tail = bone.tail
                    b.roll = bone.roll
                    b.use_deform = False
                    b.layers=layers

                    l = len(target)
                    if l > 0:
                        b.parent = target[l-1]
                        b.use_connect = True
                    else:
                        b.parent = bone.parent

                    target.append(b)
                    return False
                
                fail = False
                for bone in chain:
                    if newBone(bone, "IK", ik, boneLayerWhitelist(1)):
                        fail = True
                        break
                    if newBone(bone, "FK", fk, boneLayerWhitelist(3)):
                        fail = True
                        break
                
                ikTarget=None
                strans=None
                
                name = makeName(bone.name, "IK.target")
                stransName = makeName(bone.name, "IK.target.s_trans")
                if name in bones or stransName in bones:
                    fail = True
                else:
                    ikTarget = bones.new(name)
                    ikTarget.use_deform = False
                    ikTarget.head = ik[-1].tail
                    ikTarget.tail = ikTarget.head+Vector((0, 0, 1))
                    ikTarget.layers=boneLayerWhitelist(2)
                    
                    lastDeform=chain[-1]
                    
                    strans=bones.new(stransName)
                    strans.use_deform = False
                    strans.head=lastDeform.head
                    strans.tail=lastDeform.tail
                    strans.roll=lastDeform.roll
                    strans.parent=lastDeform.parent
                    strans.layers=boneLayerWhitelist(1)
                    
                
                if fail:
                    for bad in ik:
                        bones.remove(bad)
                    for bad in fk:
                        bones.remove(bad)
                    if ikTarget is not None:
                        bones.remove(ikTarget)
                else:
                    groups.append((
                        chain,
                        ik,
                        fk,
                        ikTarget,
                        strans
                    ))
                    
            bpy.ops.object.mode_set(mode='POSE')
            for group in groups:
                
                chain,ik,fk,ikTarget,strans=group
                
                
                pose = obj.pose
                
                poseLastIk=pose.bones[ik[-1].name]
                stransPose= pose.bones[strans.name]
                ikTargetPos=pose.bones[ikTarget.name]
                
                ikConstraint = poseLastIk.constraints.new('IK')
                ikConstraint.target = obj
                ikConstraint.subtarget = ikTarget.name
                
                ikConstraint.chain_count = len(ik)
                ikConstraint.use_stretch = False
                
                ikTargetPos.custom_shape=getIKShape()
                ikTargetPos.use_custom_shape_bone_size
                ikTargetPos.custom_shape_transform=stransPose
                onlyMove(ikTargetPos)
                
                
                stransMod=stransPose.constraints.new('COPY_TRANSFORMS')
                stransMod.target=obj
                stransMod.subtarget=ik[-1].name
                
                stransMod=stransPose.constraints.new('LIMIT_DISTANCE')
                stransMod.target=obj
                stransMod.subtarget=ikTarget.name
                stransMod.limit_mode="LIMITDIST_ONSURFACE"
                stransMod.distance=0.000001
                
                for bone in fk:
                    bone=pose.bones[bone.name]
                    bone.custom_shape=getFKShape()
                
                def copyTrans(i, bon):
                    copy = bone.constraints.new("COPY_TRANSFORMS")
                    copy.target = obj
                    copy.subtarget = bon[i].name
                    return copy
                
                ikFkName = makeName(chain[0].name,"(IK<->FK)")
                
                
                if "_RNA_UI" not in obj:
                    obj["_RNA_UI"] = {}

                obj[ikFkName] = 0.0
                obj["_RNA_UI"][ikFkName] = {
                    "min": 0.0,
                    "max": 1.0,
                    "soft_min": 0.0,
                    "soft_max": 1.0,
                    "use_soft_limits": False,
                    "is_overridable_static": True
                }
                
                sGroups=standardBoneGroups(obj)
                
                sGroups.ik(pose.bones[ikTarget.name])
                sGroups.mech(pose.bones[strans.name])
                
                for i in range(len(chain)):
                    sGroups.deform(bone)
                    bone = pose.bones[chain[i].name]
                    
                    sGroups.deform(bone)
                    sGroups.mech(pose.bones[ik[i].name])
                    sGroups.fk(pose.bones[fk[i].name])
                    
                    bone.rotation_mode="XYZ"
                    noTransform(bone)
                    clear(bone.constraints)
                    
                    copyTrans(i, ik)
                    fkCopy = copyTrans(i, fk)

                    driv = fkCopy.driver_add("influence").driver
                    driv.type = "AVERAGE"
                    
                    clear(driv.variables)
                    
                    v = driv.variables.new()
                    v.name = "influence"
                    v.type = "SINGLE_PROP"

                    t = v.targets[0]
                    t.id_type = "OBJECT"
                    t.id = obj
                    t.data_path = "[\""+ikFkName.replace('"', '\\"')+"\"]"
                
                
        count=len(groups)

        if count > 0:
            self.report({'INFO'}, "Created "+str(count)+" IK FK chain"+s(count)+"!")

        bpy.ops.object.mode_set(mode='EDIT')
        return {"FINISHED"}
