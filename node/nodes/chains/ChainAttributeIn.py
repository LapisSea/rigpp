import bpy
import os

from ... import BoneNode
from ....utils import makeId
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import updateTrees
from ...sockets.types.SocketReference import SocketReference

class ChainAttributeIn(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Chain attribute input'
    bl_icon = 'PLUS'
    
    treeRef: StringProperty()
    
    def getTree(self):
        if not self.treeRef:
            return None
        try:
            return bpy.data.node_groups[self.treeRef]
        except:
            return None
    
    def nameChange(self,ctx):
        updateTrees()
    
    def idChange(self,ctx):
        import random
        random.seed(self.id)
        base=0.4
        randomness=0.4
        self.use_custom_color=True
        self.color=(base+random.random()*randomness,base+random.random()*randomness,base+random.random()*randomness)
        updateTrees()
    
    id: IntProperty(default=-1, update=idChange)
    attrName: StringProperty(name="Name", default="MyAttribute", update=nameChange)
    
    customInputs: CollectionProperty(type=SocketReference)
    
    def getOut(self,tree):
        return tree.findNode("ChainAttributeOut",lambda nod:nod.id==self.id)
        
    def ensureDifferentNames(self,tree):
        ins=tree.nodesByType("ChainAttributeIn")
        last=None
        while last!=self.attrName:
            last=self.attrName
            for tr in ins:
                if tr==self:
                    continue
                if tr.name==self.attrName: 
                    pos=self.attrName.rfind(".")
                    if pos==-1:
                        self.attrName=self.attrName+".001"
                    else:
                        try:
                            self.attrName=self.attrName[:pos+1]+str(int(self.attrName[pos+1:])+1).zfill(3)
                        except ValueError:
                            self.attrName=self.attrName+".001"
    
    def ensureOut(self,tree):
        out=self.getOut(tree)
        
        if out==None:
            out=tree.newNode("ChainAttributeOut")
            out.id=self.id
            out.location=self.location
            out.location[0]+=400
            out.label=self.attrName
    
    def treeUpdate(self,tree):
        if self.id==-1:
            self.id=tree.newUID()
        
        self.ensureDifferentNames(tree)
        self.ensureOut(tree)
    
    def copy(self, ctx):
        self.id=-1
    
    def init(self, context):
        self.outputs.new('NodeSocketArmature', "Armature")
        self.outputs.new('NodeSocketControllerList', "Controllers")
        self.outputs.new('NodeSocketBoneList', "Base bones")
    
    def update(self):
        
        for i in range(len(self.customInputs)):
            cIn=self.customInputs[i]
            if len(self.outputs)-3<=i:
                self.outputs.new(cIn.type, cIn.name)
                continue
            
            out=self.outputs[i+3]
            
            if out.bl_idname!=cIn.type:
                self.outputs.remove(out)
                self.update()
                return
                
            if out.name!=cIn.name:
                out.name=cIn.name
        
    
    def execute(self,context, socket, data):
        
        if self.outputs[0]==socket:
            return data["armature"]
        
        if self.outputs[1]==socket:
            return data["chain"].controllers
        
        if self.outputs[2]==socket:
            return data["chain"].base
        
        for i in range(3,len(self.outputs)):
            if self.outputs[i]==socket:
                return data["customInpGet"](i-3)
        
        raise Exception("wat")
    
    def draw_buttons(self, context, layout):
        op=layout.operator("rigpp.add_node_custom_input")
        op.treeRef=self.treeRef
        op.caller=self.name
        
        layout.prop(self, 'attrName', text="")
    
    def runGroup(self,context, data):
        return self.getOut(data["tree"]).runGroup(context, data)