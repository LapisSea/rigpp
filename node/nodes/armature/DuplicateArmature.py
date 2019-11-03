import bpy
import os

from ... import BoneNode
from ....utils import (makeId, makeName, execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

from ....name_deriver import name_deriver


class DuplicateArmature(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Duplicate armature'
    bl_icon = 'PLUS'
    
    nameDerivation: EnumProperty(items=name_deriver.types, description="How to generate new armature name", update=valChange)
    nameValue: StringProperty(update=valChange)
    
    deleteExisting: BoolProperty(name="Delete existing", update=valChange)
    
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketArmature', "Armature")
        self.outputs.new('NodeSocketArmature', "New Armature")
        
        tree.endMultiChange()
        
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"nameDerivation", text="")
        if self.nameDerivation!="ANUM":
            layout.prop(self,"nameValue", text="")
        layout.prop(self,"deleteExisting")
    
    
    def execute(self,context, socket, data):
        obj=execSocket(self.inputs[0], context, data)
        if obj==None:
            return None
        
        name=name_deriver.derive(self.nameDerivation, obj.name, self.nameValue)
        copied=None
        collections=None #context.scene.master_collection
        
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
        
        oldData=copied.data
        copied.data = obj.data.copy()
        
        dataName=copied.name
        
        if oldData.users == 0:
            bpy.data.armatures.remove(oldData)
        
        if dataName in bpy.data.armatures:
            old=bpy.data.armatures[dataName]
            if old.users == 0:
                bpy.data.armatures.remove(old)
        
        
        copied.data.name=dataName
        
        for cols in copied.users_collection:
            cols.objects.unlink(copied)
        
        for cols in obj.users_collection:
            cols.objects.link(copied)
        
        return copied