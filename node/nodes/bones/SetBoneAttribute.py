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
                
                attributeTypes[k]=typ
        
        objModeSession(context, obj, "EDIT", do)
        
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
    
    def change(self,ctx):
        typ="NodeSocket"+attributeTypes[self.attr].capitalize()
        
        if len(self.inputs)<2:
            self.inputs.new(name="Value", type=typ)
        
        if self.inputs[1].bl_idname!=typ:
            self.inputs.remove(self.inputs[1])
            self.inputs.new(name="Value", type=typ)
            
        
        valChange(self,ctx)
    
    attr: EnumProperty(items=lambda s,c: attributes, name="Attribute", update=change)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"attr",text="")
    
    def update(self):
        _scrape()
    
    def init(self, context):
        _scrape()
        self.inputs.new("NodeSocketBoneList", "Bones")
        self.inputs.new("NodeSocketAny", "Value")
        self.outputs.new("NodeSocketBoneList", "Bones")
    
    def execute(self,context, socket,data):
        _scrape()
        
        bones=execSocket(self.inputs[0], context, data)
        
        def do(armature):
            value=execSocket(self.inputs[1], context, data)
            ebs=armature.data.edit_bones
            for bone in bones:
                setattr(ebs[bone[0]],self.attr,value)
        
        if bones:
            objModeSession(context,bones[0][1],"EDIT",do)
        
        return bones