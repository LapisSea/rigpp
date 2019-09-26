import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import execNode

class NodeSocketChainList(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Chain List Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.1, 0.3, 1, 0.5)
    
    def execute(self,context, data):
        if self.is_output:
            return self.node.execute(context, self, data)
        if not self.is_linked:
            return []
            
        link=self.links[0]
        return execNode(link.from_node, link.from_socket, context, data)