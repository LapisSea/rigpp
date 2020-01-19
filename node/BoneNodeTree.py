import bpy
from bpy.types import NodeTree
from ..utils import (makeId, runLater,onDepsgraph,execNode)
from mathutils import Vector
import traceback

from ..import_properties import *

def onChange(ctx):
    # def ay():
    #     valChange(None,ctx)
    
    # runLater(ay,"BoneNodeTree_onChange")
    
    # print("onChange")
    return
    
onDepsgraph(onChange)

TREE_ID=makeId("bone_node_tree")



def valChange(self,ctx):
    for g in bpy.data.node_groups:
        if g.bl_idname == TREE_ID:
            g.update()
            g.autoExec()

def updateTrees(self=None,context=None):
    for g in bpy.data.node_groups:
        if g.bl_idname == TREE_ID:
            g.update()

class BoneNodeTree(NodeTree):
    
    bl_description = "Bone Node Trees"
    bl_icon = "MESH_TORUS"
    bl_idname = TREE_ID
    bl_label = "Bone node tree"
    
    uid: IntProperty(default=1)
    autoExecute: BoolProperty(name="Auto execute", default=True)
    
    updateCount=0
    blockUpdates=False
    
    def startMultiChange(self):
        self.blockUpdates=True
    
    def endMultiChange(self):
        self.blockUpdates=False
        self.update()
    
    def newUID(self):
        u=self.uid
        self.uid+=1
        return u
    
    def nodesByType(self,type):
        type=makeId(type)
        return [n for n in self.nodes if n.bl_idname==type]
    
    def findNode(self,type=None,check=None):
        if type!=None:
            type=makeId(type)
        for node in self.nodes:
            if type!=None and node.bl_idname!=type:
                continue
            
            if check==None or check(node):
                return node
        return None
    
    def newNode(self,type):
        return self.nodes.new(makeId(type));
    
    def validateLinks(self):
        do=True
        while do:
            do=False
            
            for link in self.links:
                fromSoc=link.from_socket
                toSoc=link.to_socket
                
                def matchSoc(l,r):
                    if l.bl_idname==r.bl_idname:
                        return True
                    
                    if hasattr(l, "canCast"):
                        if l.canCast(r):
                            return True
                    
                    if hasattr(r, "canCast"):
                        if r.canCast(l):
                            return True
                    
                    return False
                
                if not matchSoc(fromSoc, toSoc):
                    c1=self._updateRules(fromSoc.node)
                    c2=self._updateRules(toSoc.node)
                    c=c1 or c2
                    if c:
                        do=True
                        break
                
                if not matchSoc(fromSoc, toSoc):
                    
                    try:
                        self.links.remove(link)
                    except:
                        do=True
                        break
                    
                    if hasattr(fromSoc, "getCastExplicit"):
                        caster=fromSoc.getCastExplicit(toSoc)
                        if caster:
                            id=makeId(caster)
                            
                            n=None
                            
                            for dup in self.nodes:
                                if dup.bl_idname==id:
                                    ok=False
                                    for link in self.links:
                                        if link.from_socket==fromSoc and link.to_socket.node==dup:
                                            ok=True
                                            break
                                    if ok:
                                        n=dup
                                        break
                            
                            if n==None:
                                n=self.nodes.new(id)
                                n.location=(fromSoc.node.location+toSoc.node.location)/2
                            
                            soc1=None
                            soc2=None
                            
                            for soc in n.inputs:
                                if matchSoc(fromSoc, soc):
                                    soc1=soc
                                    break
                            if soc1==None:
                                raise Exception("Failed to find casting input socket")
                            
                            for soc in n.outputs:
                                if matchSoc(toSoc, soc):
                                    soc2=soc
                                    break
                            if soc2==None:
                                raise Exception("Failed to find casting output socket")
                            
                            self.links.new(fromSoc, soc1)
                            self.links.new(soc2, toSoc)
                            
                            n.select=False
    
    def _updateRules(self,node):
        if hasattr(node, "rules"):
            return node.updateRules()
        return False
    
    def groupFlow(self):
        
        resolvedNodes={}
        
        def getGroupData(node):
            if hasattr(node,"groupMarkers"):
                
                markers=node.groupMarkers()
                
                if markers:
                    return (node.getGroupId(), markers)
            
            return (None, None)
        
        def flow(node, groupId):
            
            def progress(otherNode):
                
                try:
                    id=resolvedNodes[otherNode.name]
                    if groupId==id:
                        return
                    raise Exception("group conflict")
                except:
                    ...
                
                
                flow(otherNode, groupId)
            
            resolvedNodes[node.name]=groupId
            
            
            for sock in node.outputs:
                for link in sock.links:
                    progress(link.to_node)
            
            for sock in node.inputs:
                for link in sock.links:
                    progress(link.from_node)
        
        
        for node in self.nodes:
            node.use_custom_color=False
        
        for node in self.nodes:
            
            id, markers=getGroupData(node)
            if not markers:
                continue
            
            resolvedNodes[node.name]=id if "REFERENCE" in markers else -1
            
            if "START" in markers:
                for sock in node.outputs:
                    for link in sock.links:
                        flow(link.to_node, id)
            
            if "END" in markers:
                for sock in node.inputs:
                    for link in sock.links:
                        flow(link.from_node, id)
        
        ids=sorted(set(resolvedNodes.values()))
        idLen=len(ids)
            
        import colorsys
        import random
        
        defaultRGBA=bpy.context.preferences.themes["Default"].node_editor.node_backdrop
        
        defaultVal=colorsys.rgb_to_hsv(defaultRGBA[0],defaultRGBA[1],defaultRGBA[2])[2]
        
        repeats=max(1,int(pow(idLen, 0.5)))
        
        def calcColor(i):
            rep=((i%(repeats+1))/repeats)
            
            return colorsys.hsv_to_rgb(
                i/idLen,
                rep*0.5+0.25,
                pow(defaultVal,0.5+rep*0.2)
            )
        
        # colors=[calcColor(i) for i in range(idLen)]
        
        for i, id in enumerate(ids):
            
            # random.seed(id+idLen)
            # pos=random.randint(0, len(colors)-1)
            
            # idCol=colors[pos]
            # del colors[pos]
            
            idCol=calcColor(i)
            
            for name, nodeId in resolvedNodes.items():
                if id!=nodeId:
                    continue
                
                node=self.nodes[name]
                
                node.use_custom_color=True
                node.color=idCol
        
    
    def update(self):
        
        if self.blockUpdates:
            # print("INFO: Blocked update")
            return
        
        if self.updateCount>0:
            return
        
        self.updateCount+=1
        try:
            if self.name not in bpy.data.node_groups:
                print("DEB: Tree "+self.name+" not in bpy.data.node_groups, refusing to update")
                return
            
            selfAvare=False
            try:
                selfAvare=bpy.context.space_data.edit_tree==self
            except:
                pass
            
            
            if not selfAvare:
                
                def makeContext():
                    for window in bpy.context.window_manager.windows:
                        for screen in window.workspace.screens:
                            for area in screen.areas:
                                for space in area.spaces:
                                    if isinstance(space, bpy.types.SpaceNodeEditor):
                                        if space.edit_tree==self:
                                            return {
                                                'window': window, 
                                                'screen': screen,
                                                'area': area, 
                                                'space': space, 
                                                'edit_tree': space.edit_tree
                                            }
                ctx=makeContext()
                if ctx:
                    bpy.ops.rigpp.update_bone_tree({**bpy.context.copy(), **ctx})
                else:
                    print("failed to emulate tree context")
                return
            
            
            
            if hasattr(self,"node_cache"):
                del self.node_cache
            
            change=True
            maxIter=200
            limit=maxIter
            
            for node in self.nodes:
                if not isinstance( node,bpy.types.NodeReroute):
                    continue
                
                reroute=node
                inputs=reroute.inputs
                outputs=reroute.outputs
                
                def apply(l):
                    
                    if l.bl_idname in ("NodeSocketColor", inputs[0].bl_idname):
                        return False
                    
                    ins=[s.from_socket for s in inputs[0].links]
                    inputs.clear()
                    ous=[s.to_socket for s in outputs[0].links]
                    outputs.clear()
                    
                    newIn=inputs.new(l.bl_idname,l.name)
                    newOu=outputs.new(l.bl_idname,l.name)
                    
                    for s in ins:
                        self.links.new(s,newIn)
                    
                    for s in ous:
                        self.links.new(newOu,s)
                        
                    return True
                
                
                inL=inputs[0].links
                
                if inL:
                    if apply(inL[0].from_socket):
                        continue
                    
                outL=outputs[0].links
                
                if outL:
                    if apply(outL[0].to_socket):
                        continue
                
                
                
            
            while change and limit>0:
                limit-=1
                change=False
                
                for n in reversed(self.nodes):
                    c=self._updateRules(n)
                    if c:
                        change=True
            
            self.validateLinks()
            
            for n in reversed(self.nodes):
                if hasattr(n, "update"):
                    n.update()
            
            self.groupFlow()
            
            self.autoExec()
        finally:
            self.updateCount=0
    
    def get_cached(self,name, generator):
        caches=None
        if hasattr(self,"node_cache"):
            caches=self.node_cache
        else:
            caches={}
            try:
                self.node_cache=caches
            except:
                pass
        
        cached=caches.get(name)
        if cached:
            return cached
        
        cached=generator(self)
        caches[name]=cached
        return cached
    
    
    def autoExec(self):
        if getattr(self,"execute_flag",False):
            return
        
        if self.autoExecute:
            self.execute(bpy.context)
            # bpy.ops.rigpp.execute_bone_tree(bpy.context.copy())
        
    def execute(self,context):
        
        if getattr(self,"execute_flag",False):
            return
        
        self.execute_flag=True
        if hasattr(self,"run_cache"):
            del self.run_cache
        
        self.update()
        
        print("Executing...")
        
        try:
            data={
                "tree":self,
                "run_cache":{
                    "outputs":{},
                    "group_outputs":{},
                },
            }
            
            startCandidates=self.nodes
            
            for node in startCandidates:
                canBe=hasattr(node,"isTerminator") and node.isTerminator()
                
                if canBe:
                    for sock in node.outputs:
                        if sock.is_linked:
                            canBe=False
                            break
                
                if canBe:
                    execNode(
                        node,
                        node.outputs[0] if node.outputs else None,
                        context,
                        data)
            
            self.run_cache=data["run_cache"]
        finally:
            self.execute_flag=False
        
        