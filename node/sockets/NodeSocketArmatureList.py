import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

class NodeSocketArmatureList(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Armature List Node Socket'
    
    value: PointerProperty(type=bpy.types.Object)

    def draw(self, context, layout, node, text):
        def doText():
            tree=context.space_data.edit_tree
            
            if hasattr(tree,"run_cache"):
                run_cache=tree.run_cache
                try:
                    data=run_cache["outputs"][node.name][self.identifier]
                    if data:
                        return text + " ("+str(len(data)) + ")"
                except:
                    pass
            
            return text
            
        layout.label(text=doText())
    
    def draw_color(self, context, node):
        return (0.964706, 0.411765, 0.07451, 0.5)
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        if not self.is_linked:
            return []
            
        link=self.links[0]
        return execSocket(link.from_socket, context,data)