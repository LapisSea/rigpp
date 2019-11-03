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
    
    
    value: PointerProperty(type=bpy.types.Object, poll=lambda self, obj:obj.type=="ARMATURE")
    
    def init(self, context):
        self.outputs.new('NodeSocketArmature', "Armature")
    
    def draw_label(self):
        val=self.value
        if self.hide and val:
            return val.name
        else:
            return self.bl_label
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")
    
    def execute(self,context, socket, data):
        return self.value