import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)
import math

from ..BoneNodeTree import valChange
import sys

class NodeSocketBFloat(NodeSocket):
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
    
    
    def draw(self, context, layout, node, text):
        def doText():
            tree=context.space_data.edit_tree
            
            if hasattr(tree,"run_cache"):
                run_cache=tree.run_cache
                try:
                    data=run_cache["outputs"][node.name][self.identifier]
                    if data!=None:
                        return text + " ("+str(data) + ")"
                except:
                    pass
            
            return text
        
        if self.is_output:
            layout.label(text=doText())
        elif self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (161/256, 161/256, 161/256, 1)
    
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return self.value
        
        return execSocket(links[0].from_socket, context,data)