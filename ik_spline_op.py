import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone, PoseBone
from mathutils import Matrix, Vector, Euler
from mathutils.geometry import interpolate_bezier
from . import_properties import *
from . bone_shapes import *

from .bezier.bezierCurve import *


class RigPP_OT_SplineChain(bpy.types.Operator):
    bl_idname = "rigpp.create_spline_chain"
    bl_label = "Create Spline Chain"
    bl_description = "Create an IK Spline chain from control bones"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: IntProperty(name="Resolution",
                            description="Number of bones between each control bone",
                            default=3,
                            min=1,
                            max=32,
                            step=1)
    bBoneSegments: IntProperty(name="Bendy bone segments",
                               description="Number of bendy bone segments for each bone",
                               default=4,
                               min=1,
                               max=32,
                               step=1)
    dirMode: EnumProperty(name="Direction mode",
                          default="+z",
                          items=[
                              ("+x", "Bone X", "Align bezier handles to bone X (side)"),
                              ("+y", "Bone Y", "Align bezier handles to bone Y (up)"),
                              ("+z", "Bone Z", "Align bezier handles to bone Z (front)"),
                              ("-x", "Bone -X","Align bezier handles to bone -X (side)"),
                              ("-y", "Bone -Y", "Align bezier handles to bone -Y (up)"),
                              ("-z", "Bone -Z","Align bezier handles to bone -Z (front)"),
                              ("Pn", "Point next","Bezier handles take direction to next bone"),
                              ("Pa", "Point avarage","Bezier handles take avarage of direction to next and previous bone"),
                              ("Pp", "Point previous","Bezier handles take direction to previous bone"),
                          ])

    evenDistribution: BoolProperty(name="Even distribution",
                                   description="Evenly distribute bones instead of constant n/o bones between segments",
                                   default=True)
    
    @classmethod
    def poll(self, context):
        if context.mode != "EDIT_ARMATURE":
            return False
        
        for obj in getArmatures(context):
            count=0
            for bone in obj.data.edit_bones:
                if not bone.select:
                    continue
                count+=1
            
            if count>1:
                return True
            
        return False

    def execute(self, context):
        chains=[]
        
        #create bezier curves
        for obj in getArmatures(context):
            controls=[]
            
            bones=obj.data.edit_bones
            
            for bone in bones:
                if not bone.select:
                    continue
                
                controls.append(bone.name)
            
            if not controls:
                continue
            
            chain=[]
            
            curveData = bpy.data.curves.new(obj.name+".Spline", type='CURVE')
            curveData.dimensions = '3D'
            spline=curveData.splines.new('BEZIER')
            
            
            spline.bezier_points.add(len(controls)-1)
            for i, name in enumerate(controls):
                p=spline.bezier_points[i]
                bone=bones[name]
                
                p.co = bone.head
                
                p.handle_right_type=p.handle_left_type="ALIGNED"
                
                
                def next():
                    return bones[controls[i-1]] if i+1==len(controls) else bones[controls[i+1]]
                def prev():
                    return bones[controls[i+1]] if i==0 else bones[controls[i-1]]
                
                
                bezierDir={
                    "+":lambda b,axis:getattr(bone,axis+"_axis"),
                    "-":lambda b,axis:getattr(bone,axis+"_axis")*-1,
                    "P":lambda b,type:{
                        "n":lambda:next().head-b.head,
                        "a":lambda:((next().head-b.head)+(b.head-prev().head))/2,
                        "p":lambda:b.head-prev().head
                    }[type]()
                }[self.dirMode[0]](bone,self.dirMode[1])
                bezierDir.normalize()
                
                p.handle_left=p.co-bezierDir
                p.handle_right=p.co+bezierDir
                
            
            curveOB = bpy.data.objects.new(controls[-1]+".Chain Spline", curveData)
            
            context.scene.collection.objects.link(curveOB)
            
            chains.append((obj,controls,chain,curveOB))
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        active=context.view_layer.objects.active
        
        #bind bezier curve points to bones
        count=0
        for c in chains:
            obj,controls,chain,curveOB=c
            count+=1
            
            context.view_layer.objects.active = curveOB
            
            bpy.ops.object.mode_set(mode='EDIT')
            
            for i, name in enumerate(controls):
                hook=curveOB.modifiers.new(name="Hook to bone "+name, type="HOOK")
                hook.object=obj
                hook.subtarget=name
                
                points=curveOB.data.splines[0].bezier_points
                
                def set(p, b):
                    p.select_control_point=b
                    p.select_left_handle=b
                    p.select_right_handle=b
                
                set(points[i-1],False)
                set(points[i],True)
                
                bpy.ops.object.hook_assign(modifier=hook.name)
                bpy.ops.object.hook_reset(modifier=hook.name)
            
            bpy.ops.object.mode_set(mode='OBJECT')
        
        
        #generate chains and set up spline IK constraints
        for c in chains:
            obj,controls,chain,curveOB=c
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            spline=curveOB.data.splines[0]
            points=spline.bezier_points
            
            bones=obj.data.edit_bones
            resolution=self.resolution
            
            def makeBones(data):
                lastChain=None
                for boneGen in data:
                    head, tail, id, interpolation=boneGen
                    
                    def boneVec(name):
                        b=bones[name]
                        v=b.tail-b.head
                        v.normalize()
                        return v
                    
                    dir=boneVec(controls[id])*(1-interpolation)+boneVec(controls[id+1])*interpolation
                    dir.normalize()
                    
                    bone=bones.new(makeName(controls[0], "chain", True))
                    bone.bbone_segments=self.bBoneSegments
                    
                    bone.head=head
                    bone.tail=tail
                    bone.parent=lastChain
                    bone.align_roll(dir)
                    bone.use_connect = True
                    bone.use_deform = True
                    
                    lastChain=bone
                    chain.append(bone.name)
            
            def doEven():
                bezSpline=fromBlenderSpline(spline)
                iterators=list(bezSpline.getIterator(i) for i in range(len(points)-1))
                lengths  =list(i.computeLength(15) for i in iterators)
                
                partCount=len(lengths)
                totalLength=sum(lengths)
                pointCount=resolution*partCount+1
                
                def ItoP(i):
                    percent=i/max(1,pointCount-1)
                    distance=percent*totalLength
                    
                    id=-1
                    interpolation=0
                    
                    for i, length in enumerate(lengths):
                        
                        if distance<=length:
                            interpolation=distance/length
                            id=i
                            break
                        
                        distance-=length
                    
                    if id==-1:
                        interpolation=1
                        id=partCount-1
                    
                    return iterators[id].pointAt(interpolation), id, interpolation
                
                cords=list(ItoP(i) for i in range(pointCount))
                
                for i in range(len(cords)-1):
                    pos,id,interpolation=cords[i]
                    yield pos, cords[i+1][0], id, interpolation
            
            def doConstant():
                res=max(resolution-1,1)
                for i in range(len(points)-1):
                    p1=points[i]
                    p2=points[i+1]
                    
                    cords=interpolate_bezier(
                        p1.co,
                        p1.handle_right,
                        p2.handle_left,
                        p2.co,
                        resolution+1
                    )
                    
                    for j in range(resolution):
                        c1=cords[j]
                        c2=cords[j+1]
                        
                        yield c1, c2, i, j/res
            
            makeBones(doEven() if self.evenDistribution else doConstant())
            
            
            for name in controls:
                bone=bones[name]
                bone.layers=boneLayerWhitelist(2)
            
            bpy.ops.object.mode_set(mode='POSE')
            bones=obj.pose.bones
            
            groups=standardBoneGroups(obj)
            
            for name in controls:
                bone=bones[name]
                bone.custom_shape=getSplineCtrlShape()
                groups.ik(bone)
                bone.lock_scale=[True,True,False]
            
            for bone in chain:
                groups.deform(bones[bone])
            
            end:PoseBone=bones[chain[-1]]
            
            splineIk=end.constraints.new("SPLINE_IK")
            splineIk.target=curveOB
            splineIk.chain_count=len(chain)
            
            bpy.ops.object.mode_set(mode='OBJECT')
            curveOB.hide_render=curveOB.hide_viewport=True
        
        
        if count > 0:
            self.report({'INFO'}, "Created "+str(count)+" Spline chain"+s(count)+"!")
        
        bpy.ops.object.select_all(action='DESELECT')
        
        for c in chains:
            c[0].select_set(True)
        
        context.view_layer.objects.active=active
        
        bpy.ops.object.mode_set(mode='EDIT')
        return {"FINISHED"}
