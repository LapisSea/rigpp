import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)
import math

from ..BoneNodeTree import valChange
import sys

import mathutils

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketBColor(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    selfTerminator:BoolProperty()
    
    value: FloatVectorProperty(name="value", subtype="COLOR",size=4, update=valChange,min=0, max=1, default=(1,1,1,1))
    

    def drawProp(self, layout, text):
        if self.selfTerminator:
            l=layout.column()
            l.template_color_picker(self, "value",value_slider=True)
            l.prop(self, "value", text="")
        else:
            layout.prop(self, "value", text=text)
        
    def draw_color(self, context, node):
        return (199/256, 199/256, 41/256, 1)
    
    from ..RGBA import RGBA
    
    def getVal(self):
        from ..RGBA import RGBA
        return RGBA(self.value)
    
    def execute(self,context, data):
        if self.selfTerminator:
            return self.getVal()
        
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return self.getVal()
        
        return execSocket(links[0].from_socket, context,data)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None