import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,runLater,onDepsgraph,offDepsgraph)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter
from ...BoneRef import (BoneRefList,BoneRef)

attributes=[]
attributeTypes={}

def _scrape():
    if attributes:
        return
    
    print("Scraping ")
    
    context=bpy.context
    
    arm=bpy.data.armatures.new("__ARM_SCRAP")
    obj=bpy.data.objects.new("__ARM_SCRAP", arm)
    context.scene.collection.objects.link(obj)
    try:
        
        def EDIT(armature):
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
                    if typ=="bpy_prop_array":
                        typ=val[0].__class__.__name__.capitalize()+"List"
                    else:
                        typ=typ.capitalize()
                    
                    typ="NodeSocketB"+typ
                
                attributeTypes[k]=typ
        
        
        objModeSession( obj, "EDIT", EDIT)
        
    finally:
        context.scene.collection.objects.unlink(obj)
        bpy.data.objects.remove(obj)
        bpy.data.armatures.remove(arm)


def _scrape0(scene):
    try:
        offDepsgraph(_scrape0)
    except:pass
    
    _scrape()


def causeDepsgraph():
    try:
        offDepsgraph(_scrape0)
    except:
        pass
    
    if attributes:
        return
    
    runLater(causeDepsgraph)
    onDepsgraph(_scrape0)
    
    # print("Causing Depsgraph")
    bpy.context.scene.gravity=bpy.context.scene.gravity
    
    return 0

runLater(causeDepsgraph)

class SetBoneAttribute(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Set bone attribute'
    bl_icon = 'PLUS'
    
    def getAttribType(self):
        _scrape()
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
        
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketBone", "Bones")
        self.inputs.new("NodeSocketAny", "Value")
        self.outputs.new("NodeSocketBone", "Bones")
        self.change(context)
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket,data):
        _scrape()
        
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