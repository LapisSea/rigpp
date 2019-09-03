import bpy
import os

from ... import BoneNode
from ....utils import (makeId, makeName, execNode)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange


def doANUM(name,value, context):
    segments=name.split(".")
    if len(segments)==1:
        segments.append("000")
    
    if len(segments)>1:
        try:
            num=int(segments[-1])
            segments[-1]=str(num+1).zfill(3)
        except:
            segments.append("001")
            pass
    
    return ".".join(segments)

def doADDP(name,value, context):
    return makeName(name, value)
def doREMP(name,value, context):
    segments=name.split(".")
    for i in reversed(range(len(segments))):
        if segments[i]==value:
            segments.remove(i)
            break
    return ".".join(segments)
def doNEWN(name,value, context):
    return value

nameDerivationTypes=[
    ("ANUM","Append number", "The blender default way"),
    ("ADDP","Add name part", "Adds name part to the end of the name (gen + My.Armature.001 = My.Armature.gen.001"),
    ("REMP","Remove name part", "Removes name part at the end of the name (My.Armature.base.001 - base = My.Armature.001)"),
    ("NEWN", "New name", "Use a new unrelated name")
]
nameDerivators={
    "ANUM": doANUM,
    "ADDP": doADDP,
    "REMP": doREMP,
    "NEWN": doNEWN,
}

class DuplicateArmature(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Duplicate armature'
    bl_icon = 'PLUS'
    
    nameDerivation: EnumProperty(items=nameDerivationTypes, description="How to generate new armature name",default="REMP", update=valChange)
    nameValue: StringProperty(update=valChange)
    
    deleteExisting: BoolProperty(name="Delete existing", update=valChange)
    
    
    def init(self, context):
        self.inputs.new('NodeSocketArmature', "Armature")
        self.outputs.new('NodeSocketArmature', "New Armature")
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"nameDerivation", text="")
        if self.nameDerivation!="ANUM":
            layout.prop(self,"nameValue", text="")
        layout.prop(self,"deleteExisting")
    
    
    def execute(self,context, socket, data):
        obj=execNode(self.inputs[0], context, data)
        if obj==None:
            return None
        
        for arm in bpy.data.armatures:
            if arm.users == 0 and "auto clean up - rigpp" in arm:
                bpy.data.armatures.remove(arm)
        
        name=nameDerivators.get(self.nameDerivation)(obj.name, self.nameValue,context)
        copied=None
        
            
        if name in context.scene.objects:
            copied=context.scene.objects[name]
            if self.deleteExisting:
                d=copied.data
                bpy.data.objects.remove(copied)
                bpy.data.armatures.remove(d)
                copied=None
        
        if copied==None:
            copied=obj.copy()
            copied.name=name
            context.collection.objects.link(copied)
        
        data=copied.data
        copied.data = obj.data.copy()
        copied.data["auto clean up - rigpp"]=True
        
        return copied