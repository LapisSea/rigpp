import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execNode)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (valChange, updateTrees)

noAttr=[("0","- No attribute -","")]

class AddChainAttribute(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Add chain attribute'
    bl_icon = 'PLUS'
    
    treeRef: StringProperty()
    
    def getTree(self):
        if not self.treeRef:
            return None
        try:
            return bpy.data.node_groups[self.treeRef]
        except:
            return None
    
    def getAttributes(self, context=None):
        
        def generate(tree):
            nodes=tree.nodesByType("ChainAttributeIn")
            
            if not nodes:
                return noAttr
            
            result=[(str(attr.id),attr.attrName,"") for attr in nodes]
            
            result.sort(key = lambda val: val[0])
            return result
        
        tree=self.getTree()
        if not tree:
            return noAttr
        
        attributes=tree.get_cached("AttributeIns", generate)
        
        bad=True
        for attr in attributes:
            if attr[0]==str(self.attributeId):
                bad=False
                break
                
        if bad:
            tree.update_tag()
        
        return attributes
        
    
    def syncCustomInputs(self,inputs):
        
        for i in range(len(inputs)):
            cIn=inputs[i]
            if len(self.inputs)-1<=i:
                self.inputs.new(cIn.sockType,cIn.name)
                continue
            
            
            sock=self.inputs[i+1]
            
            if sock.bl_idname!=cIn.sockType:
                self.inputs.remove(sock)
                self.syncCustomInputs(inputs)
                return
                
            if sock.name!=cIn.name:
                sock.name=cIn.name
        
        if len(inputs)<len(self.inputs)-1:
            for i in range(len(inputs)+1,len(self.inputs)):
                self.inputs.remove(self.inputs[i])
        
    def validateId(self):
        try:
            s=str(self.attributeId)
            if self.attribute!=s:
                self.attribute=s
        except:
            attrs=self.getAttributes()
            if attrs!=noAttr:
                self.attribute=attrs[0][0]
            
    def update(self):
        
        self.validateId()
        
        tree=self.getTree()
        if not tree:
            return
        
        inNode=tree.findNode("ChainAttributeIn",lambda n:n.id==self.attributeId)
        
        if inNode:
            self.syncCustomInputs(inNode.customInputs)
            
    
    def onChangeAttribute(self, context):
        val=[v for v in self.getAttributes() if v[0]==self.attribute][0]
        i=int(val[0])
        if self.attributeId!=i:
            self.attributeId=i
    
    attributeId: IntProperty(update=updateTrees)
    attribute: EnumProperty(items=getAttributes, name="Attribute", update=onChangeAttribute)
    
    def getId(self):
        self.validateId()
        return self.attributeId
    
    def init(self, context):
        self.inputs.new('NodeSocketChainList', "Chains")
        self.outputs.new('NodeSocketChainList', "Chains")
    
    def draw_buttons(self, context, layout):
        op=layout.operator("rigpp.empty_chain_attribute_resolve")
        op.treeRef=self.treeRef
        op.x=self.location[0]
        op.y=self.location[1]
        op.caller=self.name
        
        # layout.label(text="Id: "+str(self.attributeId))
        
        if self.attribute!=noAttr[0]:
            layout.prop(self,"attribute", text="")
    
    def execute(self,context, socket, data):
        chains=execNode(self.inputs[0], context, data)
        
        if self.attribute!=noAttr[0]:
            for chain in chains:
                chain.attributes.append(self)
        
        return chains
    
    def getAttrName(self):
        for attr in self.getAttributes():
            if attr[0]==self.attribute:
                return attr[1]
        
        return "<ERROR>"
    
    def draw_label(self):
        if self.hide:
            return self.getAttrName()
        return self.bl_label
        