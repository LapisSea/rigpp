import bpy
import os

from ... import BoneNode
from ....utils import makeId
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

class GetArmature(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get armature'
    bl_icon = 'PLUS'
    
    def checkArmature(self,value):
        if value==None or value.data==None or value.data.__class__.__name__!="Armature":
            return False
        return True
    
    value: PointerProperty(type=bpy.types.Object, poll=checkArmature, update=valChange)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"value", text="")
        
    def init(self, context):
        self.outputs.new('NodeSocketArmature', "Armature")
    
    def execute(self,context, socket, data):
        return self.value