import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketArmatureList(BoneNodeSocketList):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Armature List Node Socket'
    
    def draw_color(self, context, node):
        return (0.964706, 0.411765, 0.07451, 0.5)
    