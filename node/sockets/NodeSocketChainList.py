import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import execNode

from .. import (BoneNodeSocket,BoneNodeSocketList)


class NodeSocketChainList(BoneNodeSocketList):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Chain List Node Socket'
    
    def draw_color(self, context, node):
        return (0.1, 0.3, 1, 0.5)
    