import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

class GetBones(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get armature bones'
    bl_icon = 'PLUS'
    
    def init(self, context):
        self.inputs.new("NodeSocketArmature", "Armature")
        self.outputs.new('NodeSocketBoneList', "Bones")
    
    
    def execute(self,context, socket, data):
        obj=execSocket(self.inputs[0], context, data)
        if obj==None:
            return []
        
        return [b for b in obj.data.bones]