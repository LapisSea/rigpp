import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,runLater,onDepsgraph,offDepsgraph)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter
from ...BoneRef import (BoneRefList,BoneRef)

from ....data_scrape import editBoneAttrs

class SetBoneAttribute(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Set bone attribute'
    bl_icon = 'PLUS'
    
    def getAttribType(self):
        return editBoneAttrs["types"][self.attr]
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBone"
        }),
        ("ADDAPTIVE_SOCKET", {
            "target":("input",1),
            "list_agnostic": True, 
            "accepted_types":lambda self:[self.getAttribType()],
            "default":lambda self:editBoneAttrs["types"][self.attr]
        }),
        ("MIRROR_TYPE", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    def updateVal(self):
        typ=self.getAttribType()
        
        if len(self.inputs)<2:
            self.inputs.new(name="Value", type=typ)
        else:
            self.setIOType(self.inputs,1, typ)
    
    def change(self,ctx):
        self.updateVal()
        
        valChange(self,ctx)
    
    attr: EnumProperty(items=lambda s,c: editBoneAttrs["enums"], name="Attribute", update=change)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"attr",text="")
    
    
    def init(self, context):
        
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketBone", "Bones")
        self.inputs.new("NodeSocketAny", "Value")
        self.outputs.new("NodeSocketBone", "Bones")
        self.change(context)
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket,data):
        
        bones=execSocket(self.inputs[0], context, data)
        single=socket.bl_idname=="NodeSocketBone"
        if not bones:
            return None if single else []
        
        if single:
            bones=BoneRefList([bones])
        
        value=execSocket(self.inputs[1], context, data)
        
        def do(armature):
            ebs=armature.data.edit_bones
            for bone in bones.refs:
                if bone:
                    eb=bone.getEditBone()
                    setattr(eb,self.attr,value)
                    bone.name=eb.name
        
        objModeSession(bones.armature,"EDIT",do)
        
        if single:
            return bones[0]
        return bones