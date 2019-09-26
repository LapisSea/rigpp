import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import execNode

class NodeSocketChain(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Chain Node Socket'
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.1, 0.3, 1, 1)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None
    
    def execute(self,context, tree):
        if self.is_output:
            return execNode(self.node,self,context,tree)
        if not self.is_linked:
            return []
            
        link=self.links[0]
        return execNode(link.from_node, link.from_socket, context, tree)