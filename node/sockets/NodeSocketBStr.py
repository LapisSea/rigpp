import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode, execSocket)
import math

from ..BoneNodeTree import valChange
import sys

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketBStr(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    selfTerminator:BoolProperty()
    
    value: StringProperty(name="value", update=valChange, options={"TEXTEDIT_UPDATE"})
    
    # Socket color
    def draw_color(self, context, node):
        return (99/256, 99/256, 199/256, 1)
    
    
    def execute(self,context, data):
        if self.selfTerminator:
            return self.value
        
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return self.value
        
        return execSocket(links[0].from_socket, context,data)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None