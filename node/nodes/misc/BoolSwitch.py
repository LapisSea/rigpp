import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class BoolSwitch(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Boolean switch'
    bl_icon = 'PLUS'
    
    def updateOut(self,tree):
        
        sType=None
        
        if self.inputs[1].bl_idname==self.inputs[2].bl_idname:
            sType=self.inputs[1].bl_idname
        else:
            sType="NodeSocketAny"
        
        if self.outputs[0].bl_idname==sType:
            return
        
        socks=[link.to_socket for link in self.outputs[0].links]
        
        self.outputs.remove(self.outputs[0])
        new=self.outputs.new(sType, "Result")
        
        for sock in socks:
            tree.links.new(new,sock)
        
    def setInType(self,pos,tree,typ):
        
        inp=self.inputs[pos]
        
        if inp.bl_idname==typ:
            return
        
        socks=[link.from_socket for link in inp.links]
        name=inp.name
        
        print(name,typ)
        
        self.inputs.remove(inp)
        new=self.inputs.new(typ,name)
        
        self.inputs.move(2,pos)
        
        for sock in socks:
            tree.links.new(sock, new)
        pass
    
    def doIn(self,pos,tree):
        inp=self.inputs[pos]
        l=inp.links
        if l:
            self.setInType(pos,tree,l[0].from_socket.bl_idname)
        else:
            self.setInType(pos,tree,"NodeSocketAny")
    
    def update(self):
        if not self.outputs:
            return
        
        tree=self.getTree()
        
        self.doIn(1,tree)
        self.doIn(2,tree)
        
        self.updateOut(tree)
        
    def init(self, context):
        self.inputs.new("NodeSocketBBool", "Condition")
        self.inputs.new("NodeSocketAny", "True")
        self.inputs.new("NodeSocketAny", "False")
        self.outputs.new("NodeSocketAny", "Result").value=True
    
    def execute(self,context, socket, data):
        condition=execSocket(self.inputs[0], context, data)
        
        return execSocket(self.inputs[1 if condition else 2], context, data)