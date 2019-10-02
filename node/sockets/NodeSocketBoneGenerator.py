import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)


class NodeSocketBoneGenerator(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Controllers Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None
    
    def draw_color(self, context, node):
        return (0.4, 0.6, 1, 1)
    