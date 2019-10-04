import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class GetListLen(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get List Length'
    bl_icon = 'PLUS'
    
    def setInput(self,type,tree):
        socks=[link.from_socket for link in self.inputs[0].links]
        
        self.inputs.clear()
        new=self.inputs.new(type, "List")
        
        for sock in socks:
            tree.links.new(new,sock)
    
    def update(self):
        tree=self.getTree()
        if self.inputs[0].bl_idname=="NodeSocketAnyList":
            links=self.inputs[0].links
            if not links:
                return
            
            socket=links[0].from_socket
            
            self.setInput(socket.bl_idname,tree)
            
        else:
            if not self.inputs[0].links:
                self.setInput("NodeSocketAnyList",tree)
        
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketAnyList", "List")
        self.outputs.new("NodeSocketBInt", "Length")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        data=execSocket(self.inputs[0], context, data)
        if not data:
            return 0
        return len(data)