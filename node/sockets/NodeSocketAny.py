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

    def draw_color(self, context, node):
        return (0.5, 0.5, 0.5, 1)
    
    def canCast(self, socket):
        return True
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None