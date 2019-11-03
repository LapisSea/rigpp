import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)
from ..BoneRef import (BoneRefList,BoneRef)

from .. import (BoneNodeSocket,BoneNodeSocketList)


class NodeSocketBoneList(BoneNodeSocketList):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone List Node Socket'
    
    def draw_color(self, context, node):
        return (0.4, 1, 1, 0.5)
        
    def getCastExplicit(self,target):
        if target.bl_idname=="NodeSocketChainList":
            return "MakeChains"
        else:
            return None
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return BoneRefList([])
        
        return execSocket(links[0].from_socket, context,data)