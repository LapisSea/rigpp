import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import execNode

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
    
    def execute(self,context, tree):
        if self.is_output:
            return execNode(self.node,self,context,tree)
        if not self.is_linked:
            return None
            
        link=self.links[0]
        return execNode(link.from_node, link.from_socket, context, tree)