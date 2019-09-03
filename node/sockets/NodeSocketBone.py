import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone


class NodeSocketBone(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        return (0.4, 1, 1, 1)
        
    def getCastExplicit(self,target):
        if target.bl_idname=="NodeSocketChainList":
            return "MakeChains"
        else:
            return None
    
    def execute(self,context, tree):
        if self.is_output:
            return self.node.execute(context, self, tree)
        
        links=self.links
        if not links:
            return None
            
        link=self.links[0]
        return link.from_node.execute(context, link.from_socket, tree)