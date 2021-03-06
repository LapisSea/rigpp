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
    
    def groupMarkers(self):
        return ("START","REFERENCE")
    
    def getGroupId(self):
        return self.id
    
    def nameChange(self,ctx):
        updateTrees()
    
    id: IntProperty(default=-1, update=updateTrees)
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
                
                if tr.attrName==self.attrName: 
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
    
    def copy(self, ctx):
        self.id=-1
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.outputs.new('NodeSocketBStr', "Name")
        
        self.outputs.new('NodeSocketArmature', "Armature")
        self.outputs.new('NodeSocketControllerList', "Controllers")
        self.outputs.new('NodeSocketBoneList', "Base bones")
        
        tree.endMultiChange()
        
    
    def update(self):
        
        tree=self.getTree()
        if self.id==-1:
            self.id=tree.newUID()
        
        self.ensureDifferentNames(tree)
        self.ensureOut(tree)
        
        for i in range(len(self.customInputs)):
            cIn=self.customInputs[i]
            if len(self.outputs)-4<=i:
                self.outputs.new(cIn.sockType, cIn.name)
                continue
            
            out=self.outputs[i+4]
            
            if out.bl_idname!=cIn.sockType:
                self.outputs.remove(out)
                self.update()
                continue
                
            if out.name!=cIn.name:
                out.name=cIn.name
        
        while len(self.customInputs)+4<len(self.outputs):
            self.outputs.remove(self.outputs[-1])
    
    def execute(self,context, socket, data):
        
        if self.outputs[0]==socket:
            return self.attrName
        
        chain=data["chain"]
        
        if self.outputs[1]==socket:
            return chain.base.armature
        
        if self.outputs[2]==socket:
            return chain.controllers
        
        if self.outputs[3]==socket:
            return chain.base
        
        for i in range(4,len(self.outputs)):
            if self.outputs[i]==socket:
                return data["customInpGet"](i-4)
        
        raise Exception("wat?")
    
    def draw_buttons(self, context, layout):
        
        from ....modify_node_custom_input import actions
        
        btns=layout.column_flow(columns=len(actions),align=True)
        
        for action in actions:
            op=btns.operator(action.bl_idname)
            op.caller=self.name
        
        
        layout.prop(self, 'attrName', text="")
    
    def runGroup(self,context, data):
        return self.getOut(data["tree"]).runGroup(context, data)