import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class Integer(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Integer value'
    bl_icon = 'PLUS'
    
    value: IntProperty(update=valChange)
    
    def init(self, context):
        self.outputs.new("NodeSocketBInt", "Value")
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"value")
    
    def execute(self,context, socket, data):
        return self.value