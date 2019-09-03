import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone

class NodeSocketAnyList(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Chain Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        return (0.5, 0.5, 0.5, 0.5)
    
    def canCast(self, socket):
        return socket.bl_idname.endswith("List")
    
    def execute(self,context, tree):
        if self.is_output:
            return self.node.execute(context, self, tree)
        if not self.is_linked:
            return []
            
        link=self.links[0]
        return link.from_node.execute(context, link.from_socket, tree)