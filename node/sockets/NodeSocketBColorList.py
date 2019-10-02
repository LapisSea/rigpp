import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode, execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)


class NodeSocketBColorList(BoneNodeSocketList):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Controllers List Node Socket'

    # Socket color
    def draw_color(self, context, node):
        return (199/256, 199/256, 41/256, 0.5)
    