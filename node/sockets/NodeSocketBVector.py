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

class NodeSocketBVector(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Bone Node Socket'
    
    selfTerminator: BoolProperty()
    value: FloatVectorProperty(name="value", subtype="XYZ", update=valChange)
    
    def draw(self, context, layout, node, text):
        def doText():
            tree=context.space_data.edit_tree
            
            if hasattr(tree,"run_cache"):
                run_cache=tree.run_cache
                try:
                    data=run_cache["outputs"][node.name][self.identifier]
                    if data!=None:
                        return text + " ({0:.3f}, {1:.3f}, {2:.3f})".format(data.x,data.y,data.z)
                except:
                    pass
            
            return text
        
        def drawVal():
            g=layout.column(align=True)
            g.prop(self, "value", index=0, text="X")
            g.prop(self, "value", index=1, text="Y")
            g.prop(self, "value", index=2, text="Z")
        
        if self.selfTerminator:
            drawVal()
        elif self.is_output:
            layout.label(text=doText())
        elif self.is_linked:
            layout.label(text=text)
        else:
            drawVal()

    def draw_color(self, context, node):
        return (99/256, 99/256, 199/256, 1)
    
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        else:
            return None