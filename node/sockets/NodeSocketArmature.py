import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketArmature(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Armature Node Socket'
    
    value: PointerProperty(type=bpy.types.Object)

    def draw(self, context, layout, node, text):
        
        def doText():
            tree=context.space_data.edit_tree
            
            if hasattr(tree,"run_cache"):
                run_cache=tree.run_cache
                try:
                    data=run_cache["outputs"][node.name][self.identifier]
                    if data:
                        return \
                        data.name \
                        if isinstance(data, bpy.types.bpy_struct) and hasattr(data,"name") \
                        else str(data)
                except:
                    pass
            
            return text
        
        if self.is_linked or self.is_output:
            
            layout.label(text=doText())
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
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return None
        
        return execSocket(links[0].from_socket, context,data)