import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,boneLayerWhitelist)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

from ....name_deriver import name_deriver
from ...BoneRef import (BoneRefList,BoneRef)

class GetBoneOwner(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get bone owner'
    bl_icon = 'PLUS'
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBone"
        }),
    ]
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketBoneList', "Bones")
        self.outputs.new('NodeSocketArmature', "Armature")
        
        tree.endMultiChange()
    
    def execute(self,context, socket,tree):
        bones=execSocket(self.inputs[0], context, tree)
        if not bones:
            return None
        
        return bones.armature