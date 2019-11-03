import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)
import math

from ..BoneNodeTree import valChange
import sys

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketBBool(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    value: BoolProperty(name="value", update=valChange)
    
    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=text)
        elif self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    def draw_color(self, context, node):
        return (178/256, 106/256, 48/256, 1)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None