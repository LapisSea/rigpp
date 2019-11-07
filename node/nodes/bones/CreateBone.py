import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,boneLayerWhitelist)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

from ....name_deriver import name_deriver
from ...BoneRef import (BoneRefList,BoneRef)

class CreateBone(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Create bone'
    bl_icon = 'PLUS'
        
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketArmature", "Armature")
        self.inputs.new("NodeSocketBStr", "Name")
        self.outputs.new("NodeSocketBone", "Bone")
        
        tree.endMultiChange()
    
    def execute(self,context, socket,tree):
        
        
        arm=execSocket(self.inputs[0], context, tree)
        if not arm:
            return None
            
        name=execSocket(self.inputs[1], context, tree)
        if not name:
            name="Bone"
        
        def dup(armature):
            new=armature.data.edit_bones.new(name)
            new.head=(0,0,0)
            new.tail=(0,0,1)
            
            return BoneRef.fromBone(armature,new)
        
        
        return objModeSession(arm, "EDIT", dup)