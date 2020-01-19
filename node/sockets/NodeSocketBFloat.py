import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)
import math

from ..BoneNodeTree import valChange
import sys

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketBFloat(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    minVal: FloatProperty(default=-2147483647)
    maxVal: FloatProperty(default=2147483647)
    
    def setRange(self,minVal=-2147483647,maxVal=2147483647):
        self.minVal=minVal
        self.maxVal=maxVal
    
    def _setval(self, val):
        new=min(self.maxVal, max(self.minVal,val))
        if new!=self._getval():
            self["value"]=new
            valChange(self,None)
    
    def _getval(self):
        return min(self.maxVal, max(self.minVal,self.get("value",0)))
    
    value: FloatProperty(name="value", set=_setval, get=_getval)
    
    
    def drawProp(self, layout, text):
        layout.prop(self, "value", text=text)
    
    def draw_color(self, context, node):
        return (161/256, 161/256, 161/256, 1)
    
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None