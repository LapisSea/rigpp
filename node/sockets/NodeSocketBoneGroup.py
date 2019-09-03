import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone


class NodeSocketBoneGroup(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Controllers Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1, 0, 0.5, 1)
    
    def execute(self,context, tree):
        if self.is_output:
            return self.node.execute(context, self, tree)
        
        links=self.links
        if not links:
            return []
            
        link=self.links[0]
        return link.from_node.execute(context, link.from_socket, tree)