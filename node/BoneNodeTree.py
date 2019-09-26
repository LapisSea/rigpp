import bpy
from bpy.types import NodeTree
from ..utils import (makeId, runLater,onDepsgraph,execNode)
from mathutils import Vector

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
            g.autoExec()
    
def updateTrees(self=None,ctx=None):
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
            
            bad=False
            
            if not matchSoc(fromSoc, toSoc):
                self.links.remove(link)
                
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
                        
    
    def update(self):
        
        
        if hasattr(self,"node_cache"):
            del self.node_cache
        
        if self.name not in bpy.data.node_groups:
            print("DEB: Tree "+self.name+" not in bpy.data.node_groups, refusing to update")
            return
        
        self.validateLinks()
        
        self.autoExec()
    
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
        if self.autoExecute:
            bpy.ops.rigpp.execute_bone_tree()
        
    def execute(self,context):
        
        if getattr(self,"execute_flag",False):
            return
        
        self.execute_flag=True
        
        # import traceback
        
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # traceback.print_stack()
        
        try:
            data={
                "tree":self,
                "run_cache":{
                    "outputs":{}
                }
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
                    
        finally:
            self.execute_flag=False
        
        