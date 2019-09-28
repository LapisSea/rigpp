import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class Color(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Color value'
    bl_icon = 'PLUS'
    
    
    def init(self, context):
        self.outputs.new("NodeSocketBColor", "Value").selfTerminator=True