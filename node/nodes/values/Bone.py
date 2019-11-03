import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)
import mathutils
from ...BoneRef import (BoneRefList,BoneRef)


class Bone(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Bone'
    bl_icon = 'PLUS'
    
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketArmature", "Armature")
        self.inputs.new("NodeSocketBStr", "Name")
        self.outputs.new("NodeSocketBone", "Bone")
        
        tree.endMultiChange()
    
    def execute(self,context, socket, data):
        armature=execSocket(self.inputs[0], context, data)
        if armature==None:
            return None
        
        name=execSocket(self.inputs[1], context, data)
        
        if not name:
            return None
        
        if name not in armature.data.bones:
            return None
        
        return BoneRef(armature, name)