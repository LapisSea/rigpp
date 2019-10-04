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
    
    def change(self,context):
        if self.wrap:
            self.inputs[1].setRange()
        else:
            self.inputs[1].setRange(0)
            
        valChange(self,context)
    
    wrap:BoolProperty(name="Wrap",default=True, update=change)
    
    
    def update(self):
        
        tree=self.getTree()
        
        typ="NodeSocketAnyList"
        
        l=self.inputs[0].links
        if l:
            typ=l[0].from_socket.bl_idname
        else:
            l=self.outputs[0].links
            if l:
                linkType=l[0].to_socket.bl_idname
                if linkType.endswith("List"):
                    tree.links.remove(l[0])
                else:
                    typ=linkType+"List"
        
        self.setIOType(self.inputs,0,typ)
        self.setIOType(self.outputs,0,typ[0:-4])
        
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketAnyList", "List")
        self.inputs.new("NodeSocketBInt", "Index")
        self.outputs.new("NodeSocketAny", "Element")
        
        tree.endMultiChange()
        
    
    def draw_buttons(self, context, layout): 
        layout.prop(self,"wrap")
    
    def execute(self,context, socket, data):
        data=execSocket(self.inputs[0], context, data)
        if not data:
            return None
            
        index=execSocket(self.inputs[1], context, data)
        l=len(data)
        if self.wrap:
            return data[index%l]
        else:
            return data[index] if index>=0 and index<l else None