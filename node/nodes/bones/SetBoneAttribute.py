import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,runLater,onDepsgraph,offDepsgraph)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

attributes=[]
attributeTypes={}

def _scrape0(scene):
    offDepsgraph(_scrape0)
    _scrape()
    
def _scrape():
    if attributes:
        return
    
    context=bpy.context
    
    arm=bpy.data.armatures.new("__ARM_SCRAP")
    obj=bpy.data.objects.new("__ARM_SCRAP", arm)
    context.scene.collection.objects.link(obj)
    try:
        
        def do(armature):
            bone=armature.data.edit_bones.new("bone")
            
            keys=[]
            for k in dir(bone):
                val=getattr(bone,k)
                try:
                    setattr(bone, k,val)
                except:
                    continue
                
                typ=val.__class__.__name__
                
                
                attributes.append((k," ".join([s.capitalize() for s in k.split("_")]),""))
                
                if typ:
                    typ="NodeSocketB"+typ.capitalize()
                
                attributeTypes[k]=typ
        
        objModeSession( obj, "EDIT", do)
        
    finally:
        context.scene.collection.objects.unlink(obj)
        bpy.data.objects.remove(obj)
        bpy.data.armatures.remove(arm)
    

onDepsgraph(_scrape0)

def fuc():
    bpy.context.scene.gravity=bpy.context.scene.gravity
runLater(fuc)

class SetBoneAttribute(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Set bone attribute'
    bl_icon = 'PLUS'
    
    def getAttribType(self):
        return attributeTypes[self.attr]
    
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
            "default":lambda self:attributeTypes[self.attr]
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
    
    attr: EnumProperty(items=lambda s,c: attributes, name="Attribute", update=change)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"attr",text="")
    
    def update(self):
        _scrape()
        # self.updateVal()
    
    def init(self, context):
        self.inputs.new("NodeSocketBone", "Bones")
        self.inputs.new("NodeSocketAny", "Value")
        self.outputs.new("NodeSocketBone", "Bones")
        self.change(context)
    
    def execute(self,context, socket,data):
        _scrape()
        
        
        bones=execSocket(self.inputs[0], context, data)
        single=socket.bl_idname=="NodeSocketBone"
        if not bones:
            return None if single else []
        
        if single:
            bones=[bones]
        
        value=execSocket(self.inputs[1], context, data)
        
        def do(armature):
            ebs=armature.data.edit_bones
            for i in range(len(bones)):
                bone=bones[i]
                if bone:
                    eb=ebs[bone[0]]
                    setattr(eb,self.attr,value)
                    bones[i]=(eb.name,armature)
        
        b=next(bo for bo in bones if bo!=None)
        armature=b[1]
        
        objModeSession(armature,"EDIT",do)
        
        if single:
            return bones[0]
        return bones