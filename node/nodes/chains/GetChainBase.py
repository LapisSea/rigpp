import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange


class GetChainBase(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get chain base bones'
    bl_icon = 'PLUS'
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketChain', "Chain")
        self.outputs.new('NodeSocketBoneList', "Base")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        chain=execSocket(self.inputs[0], context, data)
        if not chain:
            return []
        
        return chain.base.copy()