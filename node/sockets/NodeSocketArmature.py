import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone

class NodeSocketArmature(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Armature Node Socket'
    
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
        return (0.964706, 0.411765, 0.07451, 1)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        elif target.bl_idname=="NodeSocketBoneList":
            return "GetBones"
        else:
            return None
    
    def execute(self,context, data):
        if not self.is_linked and not self.is_output:
            return self.value
        if self.is_output:
            return self.node.execute(context, self, data)
        
        link=self.links[0]
        return link.from_node.execute(context, link.from_socket, data)