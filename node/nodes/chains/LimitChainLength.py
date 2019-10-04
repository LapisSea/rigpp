import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange


class LimitChainLength(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Limit chain length'
    bl_icon = 'PLUS'
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        cin=self.inputs.new('NodeSocketChainList', "Chains")
        min=self.inputs.new('NodeSocketInt', "Min length")
        min.default_value=2
        cout=self.outputs.new('NodeSocketChainList', "Chains")
        
        self.internal_links.new(cin,cout)
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        chains=execSocket(self.inputs[0], context, data)
        length=execSocket(self.inputs[1], context, data)
        
        return [c for c in chains if len(c.base)>=length]