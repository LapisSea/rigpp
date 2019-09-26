import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import execNode

class NodeSocketArmatureList(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Armature List Node Socket'
    
    value: PointerProperty(type=bpy.types.Object)

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text=text)
        else:
            if self.value == None:
                layout.label(text=text)
                layout.prop(self, "value", text="")
            else:
                layout.prop(self, "value", text="")
    
    def draw_color(self, context, node):
        return (0.964706, 0.411765, 0.07451, 0.5)
    
    def getCastExplicit(self,target):
        if target.bl_idname=="NodeSocketBoneList":
            return "GetBones"
        else:
            return None
    
    def execute(self,context, tree):
        if self.is_output:
            return execNode(self.node,self,context,tree)
        if not self.is_linked:
            return []
            
        link=self.links[0]
        return execNode(link.from_node, link.from_socket, context, tree)