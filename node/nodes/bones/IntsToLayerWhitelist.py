import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

class IntsToLayerWhitelist(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Ints To Layer Whitelist'
    bl_icon = 'PLUS'
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBInt"],
            "default":"NodeSocketBIntList"
        }),
    ]
    
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketBIntList', "Layer numbers")
        self.outputs.new('NodeSocketBBoolList', "Layers")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket,tree):
        layers=execSocket(self.inputs[1], context, tree)
        
        if not isinstance(layers, list):
            layers=[layers]
        
        return [i in layers for i in range(20)]