import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import execNode

from .. import (BoneNodeSocket,BoneNodeSocketList)


class NodeSocketController(NodeSocket):
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
        return (0.4, 1, 0.5, 1)
    
    def execute(self,context, tree):
        if self.is_output:
            return execNode(self.node,self,context,tree)
        
        links=self.links
        if not links:
            return []
            
        link=self.links[0]
        return execNode(link.from_node, link.from_socket, context, tree)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None