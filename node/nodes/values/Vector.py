import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)
import mathutils


class Vector(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Vector value'
    bl_icon = 'PLUS'
    
    
    def init(self, context):
        self.outputs.new("NodeSocketBVector", "Value").selfTerminator=True
    
    # def execute(self,context, socket, data):
    #     return self.outputs[0].value