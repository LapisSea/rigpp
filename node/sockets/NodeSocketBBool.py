import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)
import math

from ..BoneNodeTree import valChange
import sys

class NodeSocketBBool(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    value: BoolProperty(name="value", update=valChange)
    
    
    def draw(self, context, layout, node, text):
        if self.is_output:
            layout.label(text=text)
        elif self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (178/256, 106/256, 48/256, 1)
    
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return self.value
            
        return execSocket(links[0].from_socket, context,data)