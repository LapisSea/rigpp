import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class GetListElement(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get List Element'
    bl_icon = 'PLUS'
    
    def setOutput(self,type,tree):
        socks=[link.to_socket for link in self.outputs[0].links]
        
        self.outputs.clear()
        new=self.outputs.new(type[0:-4] if type.endswith("List") else type, "Element")
        
        for sock in socks:
            tree.links.new(new,sock)
            
    def setInput(self,type,tree):
        socks=[link.from_socket for link in self.inputs[0].links]
        
        self.inputs.clear()
        new=self.inputs.new(type, "List")
        self.inputs.new("NodeSocketInt", "Index")
        
        for sock in socks:
            tree.links.new(new,sock)
    
    def treeUpdate(self,tree):
        if self.inputs[0].bl_idname=="NodeSocketAnyList":
            links=self.inputs[0].links
            if not links:
                return
            
            socket=links[0].from_socket
            
            self.setInput(socket.bl_idname,tree)
            self.setOutput(socket.bl_idname[0:-4],tree)
            
        else:
            if not self.inputs[0].links:
                self.setInput("NodeSocketAnyList",tree)
                self.setOutput("NodeSocketAny",tree)
        
    def init(self, context):
        self.inputs.new("NodeSocketAnyList", "List")
        self.inputs.new("NodeSocketInt", "Index")
        self.outputs.new("NodeSocketAny", "Element")
    
    def draw_buttons(self, context, layout): 
        if self.inputs[0].bl_idname=="NodeSocketUndefined":
            layout.label(text="Connect any List")
    
    def execute(self,context, socket, data):
        list=execSocket(self.inputs[0], context, data)
        
        return list[self.index]