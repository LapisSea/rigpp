import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode, execSocket)
import math

from ..BoneNodeTree import valChange
import sys

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketBVector(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    selfTerminator: BoolProperty()
    value: FloatVectorProperty(name="value", subtype="XYZ", update=valChange)
    
    def drawProp(self, layout, text):
        g=layout.column(align=True)
        g.prop(self, "value", index=0, text="X")
        g.prop(self, "value", index=1, text="Y")
        g.prop(self, "value", index=2, text="Z")
    

    def draw_color(self, context, node):
        return (99/256, 99/256, 199/256, 1)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None