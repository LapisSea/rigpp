import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketAny(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Any Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.5, 0.5, 0.5, 1)
    
    def canCast(self, socket):
        return True