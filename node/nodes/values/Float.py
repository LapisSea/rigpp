import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class Float(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Float value'
    bl_icon = 'PLUS'
    
    value: FloatProperty(update=valChange)
    
    def init(self, context):
        self.outputs.new("NodeSocketBFloat", "Value")
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"value")
    
    def execute(self,context, socket, data):
        return self.value