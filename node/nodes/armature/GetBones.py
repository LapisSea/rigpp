import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange
from ...BoneRef import (BoneRefList,BoneRef)

class GetBones(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get armature bones'
    bl_icon = 'PLUS'
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketArmature", "Armature")
        self.outputs.new('NodeSocketBoneList', "Bones")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        obj=execSocket(self.inputs[0], context, data)
        if obj==None:
            l=BoneRefList([])
            l.armature=obj
            return l
        
        return BoneRefList([BoneRef(obj, b.name) for b in obj.data.bones])