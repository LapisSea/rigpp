import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)


class NodeSocketBoneGeneratorList(NodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Controllers List Node Socket'
    
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

    # Socket color
    def draw_color(self, context, node):
        return (0.4, 0.6, 1, 0.5)
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return []
            
        return execSocket(links[0].from_socket, context,data)