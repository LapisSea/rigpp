import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)


class NodeSocketBoneGroup(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Controllers Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1, 0, 0.5, 1)
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return []
            
        return execSocket(links[0].from_socket, context,data)