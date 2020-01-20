import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,boneLayerWhitelist)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

from ....name_deriver import name_deriver
from ...BoneRef import (BoneRefList,BoneRef)

from ....data_scrape import boneConstraints

class DefineConstraint(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Define Constraint'
    bl_icon = 'PLUS'
    
    
    def getAttribs(self):
        return boneConstraints["types"][self.attr]
    
    def updateVal(self):
        tree=self.getTree()
        tree.startMultiChange()
        
        i=0
        for name,typ in self.getAttribs().items():
            if len(self.inputs)<=i:
                self.inputs.new('NodeSocketAny', name)
            
            self.setIOType(self.inputs,i, typ)
            i+=1
            
        while len(self.inputs)>i:
            self.inputs.remove(self.inputs[-1])
        
        tree.endMultiChange()
    
    def change(self,ctx):
        self.updateVal()
        
        valChange(self,ctx)
    
    def getItems(self,ctx=None):
        es=boneConstraints["enums"]
        # print(es[0])
        return es
    
    attr: EnumProperty(items=getItems, name="Attribute", update=change)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"attr",text="")
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.outputs.new('NodeSocketConstraint', "Constraint")
        
        tree.endMultiChange()
    
    def execute(self,context, socket,tree):
        class ConstraintDef:
            
            def __init__(self,name,data): 
                self.name=name
                self.data=data
            
            def applyAttributes(self, constraint):
                for key,value in self.data.items():
                    try:
                        setattr(constraint, key, value)
                    except:
                        pass
        
        data={}
        for i,inp in enumerate(self.inputs):
            data[inp.name]=execSocket(inp, context, data)
        
        return ConstraintDef(self.attr,data)