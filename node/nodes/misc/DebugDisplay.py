import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket,wrap)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class DebugDisplay(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Debug display'
    bl_icon = 'PLUS'
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "default":"NodeSocketAny",
            "auto_rename":False
        }),
    ]
    
    def isTerminator(self):
        return True
    
    data: StringProperty()
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketAny", "To display")
        
        tree.endMultiChange()
        
    
    def update(self):
        
        links=self.inputs[0].links
        typ="NodeSocketAny"
        if links:
            typ=links[0].from_socket.bl_idname
        
        self.setIOType(self.inputs,0,typ)
        
    
    def draw_buttons(self, context, layout): 
        
        lines=wrap(self.width/6, self.data)
        
        if not lines:
            lines.append("<EMPTY>")
            
        
        row=layout.row(align = True)
        
        for var in lines:
            row = layout.row(align = True)
            row.alignment = 'EXPAND'
            l=row.label(text=var)
            
    
    def execute(self,context, socket, data):
        objData=execSocket(self.inputs[0], context, data)
        
        if not isinstance(objData, list):
            objData=[objData]
        
        self.data="\n".join([
            (d.__class__.__name__+": "+d.name 
            if isinstance(d, bpy.types.bpy_struct)
            else 
            str(d)).replace("\t","    ") for d in objData])
        
        return objData