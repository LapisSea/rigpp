import bpy
from bpy.types import Object, Modifier, ArmatureModifier, Context
import math
import re

def s(count):
    return "s" if count != 1 else ""

def getArmatures(ctx: Context) -> list:
    result = []
    
    def get(obj: Object, result: list):
        if obj is None:
            return
        
        if obj.type == "ARMATURE":
            result.append(obj)
            return
        
        fail = True
        
        for e in obj.modifiers:
            if isinstance(e, ArmatureModifier) and e.object is not None:
                result.append(e.object)
                fail = False
                continue
        
        if fail:
            get(obj.parent, result)
    
    for obj in ctx.selected_objects:
        get(obj, result)
    
    return result


def hasArmatureContext(ctx: Context) -> bool:
    return len(getArmatures(ctx)) > 0


def findDirection(name: str):
    segments = name.split(".")

    for segment in segments:
        for e in ["L", "R", "Bk", "Fr", "Top", "Bot"]:
            if e == segment.lower().capitalize():
                return e
    return None


def isDirection(name: str):
    return findDirection(name) is not None


def reverseDirection(str: str):
    return {
        "l":   "R",
        "r":   "L",
        "bk":  "Fr",
        "fr":  "Bk",
        "top": "Bot",
        "bot": "Top"
    }[str.lower()]


def findChains(bones):
    chains = []
    for bone in bones:
        if bone.select and bone.use_deform:

            boneAdded = False
            for chain in chains:
                if bone in chain:
                    boneAdded = True
                    break
            if boneAdded:
                continue

            chain = [bone]

            while True:
                found = None
                for b in chain[len(chain)-1].children:
                    if b.use_deform and b.use_connect and b.select:
                        found = b
                        break

                if found is None:
                    break
                else:
                    chain.append(found)

            if len(chain) == 1:
                while True:
                    found = None
                    for b in chain[len(chain)-1].children:
                        if b.use_deform and b.use_connect:
                            found = b
                            break

                    if found is None:
                        break
                    else:
                        chain.append(found)

            chains.append(chain)

    return chains


def isGenNumber(segment: str):
    return segment.isnumeric() and segment.startswith("0")

def makeName(name, addon, removeNum=False):
    
    segments = name.split(".")
    insertPos=len(segments)-1
    
    if insertPos>0 and isGenNumber(segments[insertPos]):
        insertPos-=1
    if  insertPos>0 and isDirection(segments[insertPos]):
        insertPos-=1
    
    segments.insert(insertPos+1,addon)
    
    if removeNum:
        for segment in segments:
            if isGenNumber(segment):
                segments.remove(segment)
    
    return ".".join(segments)

class IKFKChain(object):
    
    name:str
    obj:Object
    
    def __init__(self,name,obj,deform):
        self.name=name
        self.obj=obj
        self._deform=deform
    
    def deform(self):
        return self._deform
    
    def fk(self):
        if not hasattr(self, "_fk"):
            self._fk=list(makeName(b,"FK") for b in self.deform())
        
        return self._fk
    
    def ik(self):
        if not hasattr(self, "_ik"):
            self._ik=list(makeName(b,"IK") for b in self.deform())
        
        return self._ik
    
    def ikTarget(self):
        if not hasattr(self, "_ikT"):
            self._ikT=makeName(self.deform()[-1],"IK.target")
        
        return self._ikT
    
    def ikTargetSTrans(self):
        if not hasattr(self, "_ikTP"):
            self._ikTP=makeName(self.deform()[-1],"IK.target.s_trans")
        
        return self._ikT
    
    def control(self):
        if not hasattr(self, "_ct"):
            for fc in self.obj.animation_data.drivers:
                p=fc.data_path
                if p.startswith('["') and p.endswith('"]') and p[2:-2]==self.name:
                    t=fc.driver.variables[0].targets[0]
                    self._ct=t.bone_target
        
        return self._ct

def findCreatedChains(context) -> list:
    result = []
    
    for obj in getArmatures(context):
        
        
        bones     = obj.data.edit_bones
        poseBones = obj.pose.bones
        
        editMode=context.mode=="EDIT_ARMATURE"
        objectMode=context.mode=="OBJECT"
        
        if objectMode: 
            bones=obj.data.bones
        elif not editMode:
            bones=poseBones
        
        for bone in bones:
            if editMode or objectMode:
                if not bone.select:
                    continue
            else:
                if bone not in context.selected_pose_bones:
                    continue
            
            def cleanAddonName(name):
                if ".IK.target.s_trans." in name:
                    return name.replace(".IK.target.s_trans.", ".")
                elif name.endswith(".IK.target.s_trans"):
                    return name.replace(".IK.target.s_trans", "")
                    
                elif ".IK.target." in name:
                    return name.replace(".IK.target.", ".")
                elif name.endswith(".IK.target"):
                    return name.replace(".IK.target", "")
                    
                elif ".FK." in name:
                    return name.replace(".FK.", ".")
                elif name.endswith(".FK"):
                    return name.replace(".FK", "")
                    
                elif ".IK." in name:
                    return name.replace(".IK.", ".")
                elif name.endswith(".IK"):
                    return name.replace(".IK", "")
                
                return name
            
            name: str = cleanAddonName(bone.name)
            if name not in bones:
                continue
            
            deformStart=bones[name] 
            
            
            def posify(bone): return poseBones[bone.name] if bone.name in poseBones else None
            
            def findChainProp(pBone):
                if pBone is None:
                    return None
                
                constraints=pBone.constraints
                for constraint in constraints:
                    
                    if constraint.type!="COPY_TRANSFORMS":
                        continue
                    
                    if constraint.target!=obj:
                        continue
                    
                    for d in obj.animation_data.drivers:
                        if d.data_path!='pose.bones["'+pBone.name+'"].constraints["'+constraint.name+'"].influence':
                            continue
                        
                        dp=d.driver.variables[0].targets[0].data_path
                        
                        if dp.startswith('["') and dp.endswith('"]'):
                            return dp[2: -2]
                    
                return None
            
            chainName=findChainProp(posify(deformStart))
            
            if chainName is None:
                continue
            if any(c.name==chainName for c in result):
                continue
            
            def isSameCain(bone):
                if bone is None:
                    return False
                    
                pBone=posify(bone)
                
                return findChainProp(pBone)==chainName
            
            deformChain=[deformStart]
            
            while isSameCain(deformStart.parent):
                deformStart=deformStart.parent
                deformChain.insert(0,deformStart)
            
            while True:
                lastBone=deformChain[-1]
                
                next=None
                for child in lastBone.children:
                    if isSameCain(child):
                        next=child
                        break
                
                if next is None:
                    break
                
                deformChain.append(next)
            
            result.append(IKFKChain(chainName,obj,list(b.name for b in deformChain)))
    
    
    return result

def clear(col):
    while not(not col):
        col.remove(col[-1])

def onlyMove(poseBone, moveRestriction=None):
    if moveRestriction is not None:
        poseBone.lock_location=moveRestriction
    poseBone.lock_rotation=[True,True ,True]
    poseBone.lock_scale   =[True,True ,True]
    
def noTransform(poseBone):
    poseBone.lock_location=[True,True ,True]
    poseBone.lock_rotation=[True,True ,True]
    poseBone.lock_scale   =[True,True ,True]

def makeOrGetCollection(collectionName, parentCollection=None):
    if parentCollection is None:
        parentCollection=bpy.context.scene.collection
    
    if collectionName in bpy.data.collections:
        return (bpy.data.collections[collectionName], False)
    
    col = bpy.data.collections.new(collectionName)
    parentCollection.children.link(col) 
    return (col, True)

def newMeshObject(name,collection,verts=[],edges=[],faces=[]):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,edges,faces)
    obj=bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


from . bone_shapes import *

def standardBoneGroups(armature):
    
    class StdGroups():
        def __init__(self, armature):
             self.__armature=armature
        
        def __get(self,name,num,shapeGetter, bone):
            pose=self.__armature.pose
            g=pose.bone_groups
            gr=None
            
            if name in g:
                gr=g[name]
            else:
                gr=g.new(name=name)
                gr.color_set="THEME"+num
            
            if bone is not None:
                bone.bone_group=gr
                bone.custom_shape=None if shapeGetter is None else shapeGetter()
            
            return gr
            
        def ik(self, bone=None):
            self.__get("IK","02", getIKShape, bone)
        def fk(self, bone=None):
            return self.__get("FK","04",getFKShape, bone)
        def mech(self, bone=None):
            return self.__get("Mech","13",None, bone)
        def deform(self, bone=None):
            return self.__get("Deform","03",None, bone)
        def ctrl(self, bone=None):
            return self.__get("Ctrl","10",getCtrlShape, bone)
        def ctrlP(self, bone=None):
            return self.__get("Ctrl.p","13",getCtrlPShape, bone)
        def tweak(self, bone=None):
            return self.__get("Tweak","01",getTweakShape, bone)
    
    return StdGroups(armature)

def boneLayerWhitelist(*indices):
    layers=[]
    for i in range(32):
        layers.append(i in indices)
    return layers

def invertSingleVariableDriver(d):
    invert=True
    varName=d.variables[0].name
    
    if d.type!="SCRIPTED":
        invert=True
    else:
        invert=re.match("(0(.0*)?\\+)?"+varName+"(\\+0(.0*)?)?", d.expression.replace(" ", ""))
    
    if invert:
        d.type="SCRIPTED"
        d.expression="1-"+varName
    else:
        d.type="AVERAGE"

def findCreatedSplineChains(context):
    editMode=context.mode=="EDIT_ARMATURE"
    poseMode=context.mode=="POSE"
    
    def findBone(mod):
        if mod.type!="HOOK":
            return None
        
        if mod.object.type!="ARMATURE":
            return None
        
        if not mod.subtarget:
            return None
        
        name=mod.subtarget
        armature=mod.object
        
        if name in armature.data.edit_bones if editMode else armature.pose.bones:
            return armature,name
        
        return None
    
    class SplineChain():
        
        def __init__(self, curve, armature):
            self.curve=curve
            self.armature=armature
            self.__controls=[]
            
            for mod in self.curve.modifiers:
                obj,bone=findBone(mod)
                if bone is None or obj != self.armature:
                    continue
                
                self.__controls.append(bone)
            
        
        def controls(self):
            return self.__controls
        
        def chain(self):
                
            if not hasattr(self, "__chain"):
                editM=True#bpy.context.mode=="EDIT_ARMATURE"
                if editM:
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                self.__chain=[]
                for bone in self.armature.pose.bones:
                    size=0
                    for constraint in bone.constraints:
                        if constraint.type=="SPLINE_IK":
                            if constraint.target!=self.curve:
                                continue
                            size=constraint.chain_count
                            break
                    
                    if size>0:
                        self.__chain.append(bone.name)
                        for i in range(size-1):
                            last=self.armature.data.bones[self.__chain[0]]
                            if not last.use_connect or last.parent is None:
                                break
                            self.__chain.insert(0,last.parent.name)
                        break
                
                if editM:
                    bpy.ops.object.mode_set(mode='EDIT')
            return self.__chain
        
    
    chains=[]
    
    def doCurve(curve):
        for mod in curve.modifiers:
            obj,bone=findBone(mod)
            
            if bone is not None:
                
                if any(c.armature==obj and bone in c.controls() for c in chains):
                    continue
                
                c=SplineChain(curve,obj)
                if not(not c.chain):
                    chains.append(c)
    
    def doArmature(armature):
        
        for bone in armature.data.edit_bones if editMode else armature.pose.bones:
            if not bone.select if editMode else bone.bone.select:
                continue
            
            found=False
            for ob in context.scene.objects:
                if ob.type == 'CURVE':
                    
                    for modifier in ob.modifiers:
                        if modifier.type!="HOOK":
                            continue
                            
                        hook=modifier
                        
                        if hook.object!=armature:
                            continue
                        if hook.subtarget!=bone.name:
                            continue
                        doCurve(ob)
                        found=True
                        break
            
            if found:
                continue
                
            if not editMode:
                def check(b):
                    for constraint in b.constraints:
                        if constraint.type=="SPLINE_IK":
                            if constraint.target is not None:
                                doCurve(constraint.target)
                                return True
                    return False
                
                while bone is not None:
                    if check(bone):
                        break
                    
                    fail=True
                    for child in bone.children:
                        if child.bone.use_connect:
                            bone=child
                            fail=False
                            break
                    
                    if fail:
                        break
    
    
    for obj in context.selected_objects:
        if obj.type=="CURVE":
            doCurve(obj)
        elif obj.type=="ARMATURE":
            doArmature(obj)
    
    return chains

def debugPoints(points):
    if not points:
        return
    
    col, new = makeOrGetCollection("dev debug points")
    for o in col.objects:
        pass
    for p in points:
        obj=bpy.data.objects.new("test", None)
        col.objects.link(obj)
        obj.location=p

def getRelevantBones(armature, ctx):
    return armature.data.edit_bones if ctx.mode=="EDIT_ARMATURE" else armature.pose.bones

def tryMirrorName(name):
    dir = findDirection(name)
    if dir is None:
        return name

    reverseDir = reverseDirection(dir)
    if "."+dir+"." in name:
        return name.replace("."+dir+".", "."+reverseDir+".")
    else:
        return name.replace("."+dir, "."+reverseDir)


ADDON_PREFIX="rigpp"

def makeId(name):
    return ADDON_PREFIX+"."+name


def objModeSession(obj,mode,session, *more):
    context=bpy.context
    
    oldActive=context.view_layer.objects.active
    oldMode=context.mode
    
    def do(m,s):
        bpy.ops.object.mode_set(mode=m, toggle=False)
        return s(obj)
        
    diffOb=oldActive != obj
    
    if diffOb and oldActive and oldMode!="OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    
    bpy.ops.object.select_all(action='DESELECT')
    
    
    context.view_layer.objects.active = obj
    
    result=do(mode,session)
    for i in range(int(len(more)/2)):
        do(more[i*2], more[i*2+1])
    
    valids=['OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'PARTICLE_EDIT', 'POSE']
    
    if oldMode not in valids:
        for valid in valids:
            if oldMode.startswith(valid):
                oldMode=valid
                break
    
    if diffOb:
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    if oldActive:
        oldActive.select_set(state=True)
        context.view_layer.objects.active = oldActive
        bpy.ops.object.mode_set(mode=oldMode, toggle=False)
    
    
    
    return result

def execNode(node, socket, context, data):
    
    cache=data["run_cache"]["outputs"]
    
    if node.name in cache:
        sockets=cache[node.name]
        if socket==None and sockets["__"]:
            return sockets["__"]
        if socket.identifier in sockets:
            return sockets[socket.identifier]
    
    
    result=node.execute(context, socket, data)
    
    sockets=None
    if node.name in cache:
        sockets=cache[node.name]
    else:
        sockets=dict()
        cache[node.name]=sockets
        
    sockets[socket.identifier if socket!=None else "__"]=result
    
    return result
    
def execSocket(socket, context, data):
    node=socket.node
    if node.bl_idname=="NodeReroute":
        ins=node.inputs[0]
        links=ins.links
        if links:
            link=links[0]
            return execSocket(link.from_socket, context, data)
        if socket.bl_idname.endswith("List"):
            return []
        return None
    
    # if socket.bl_idname in ("NodeSocketInt","NodeSocketFloat","NodeSocketBool"):
        
    #     if socket.is_output:
    #         return socket.node.execute(context, node, data)
        
    #     links=socket.links
    #     if not links:
    #         return socket.default_value
            
    #     link=socket.links[0]
    #     return execNode(link.from_node, link.from_socket, context, tree)
    return socket.execute(context, data)

import queue
from threading import Lock

runQueue = queue.Queue()
runMap = {}
__runmaplock = Lock()

depsgraphList =[]

def runLater(fun,key=None):
    if key!=None:
        __runmaplock.acquire()
        if key not in runMap:
            runMap[key]=fun
        __runmaplock.release()
    else:
        runQueue.put(fun)

def queuedRun():
    if runMap:
        __runmaplock.acquire()
        for fun in runMap.values():
            fun()
        runMap.clear()
        __runmaplock.release()
    
    while not runQueue.empty():
        fun=runQueue.get()
        try:
            fun()
        except:
            import traceback
            traceback.print_exc()
    return 1/60.0


def onDepsgraph(fun):
    depsgraphList.append(fun)

def offDepsgraph(fun):
    depsgraphList.remove(fun)

def depsgraphRun(ctx):
    for fun in depsgraphList:
        fun(ctx)
    
def reg():
    bpy.app.handlers.depsgraph_update_post.append(depsgraphRun)
    bpy.app.timers.register(queuedRun)
    
def dereg():
    try:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraphRun)
    except:
        pass
    depsgraphList.clear()
    
    try:
        bpy.app.timers.unregister(queuedRun)
    except:
        pass

def wrap(width, text):
    
    lines = []
    
    line=""
    
    block=""
    
    for c in text:
        
        if c=="\n":
            line+=block
            lines.append(line)
            
            line=""
            block=""
            continue
        
        if len(block)>0:
            if block[-1].isspace():
                if c.isspace():
                    if len(line)+len(block)>width:
                        lines.append(line)
                        line=""
                    block+=c
                    continue
                else:
                    line+=block
                    block=c
                    continue
        
        if len(line)>0 and len(line)+len(block)>width:
            lines.append(line)
            line=""
        block+=c
        
    
    if len(block)>0:
        if len(line)>0 and len(line)+len(block)>width:
            lines.append(line)
            line=""
        line+=block
    
    if len(line)>0:
        lines.append(line)
    
    return lines
