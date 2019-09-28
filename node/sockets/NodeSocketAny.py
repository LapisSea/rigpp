import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

class NodeSocketAny(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Any Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        return (0.5, 0.5, 0.5, 1)
    
    def canCast(self, socket):
        return True
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        if not self.is_linked:
            return None
            
        links=self.links
        if not links:
            return None
        
        return execSocket(links[0].from_socket, context,data)