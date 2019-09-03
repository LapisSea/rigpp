import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone


class NodeSocketBoneGenerator(NodeSocket):
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
        return (0.4, 0.6, 1, 1)
    
    def execute(self,context, tree):
        if self.is_output:
            return self.node.execute(context, self, tree)
        
        links=self.links
        if not links:
            return []
            
        link=self.links[0]
        return link.from_node.execute(context, link.from_socket, tree)