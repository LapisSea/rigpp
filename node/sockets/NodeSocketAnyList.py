import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketAnyList(BoneNodeSocketList):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Chain Node Socket'
    
    def draw_color(self, context, node):
        return (0.5, 0.5, 0.5, 0.5)
    
    def canCast(self, socket):
        return socket.bl_idname.endswith("List")
    