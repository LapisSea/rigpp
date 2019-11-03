import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *
from ....utils import (makeName,objModeSession,boneLayerWhitelist)

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange


class ApplyController(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Apply Controller'
    bl_icon = 'PLUS'
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",1),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBoneList"
        }),
        ("MIRROR_TYPE", {
            "from": ("input",1),
            "to": ("output",0)
        }),
    ]
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketController', "Controller")
        self.inputs.new('NodeSocketBoneList', "Bones")
        
        self.outputs.new('NodeSocketBoneList', "Bones")
        
        tree.endMultiChange()
        
        
    def execute(self,context, socket, data):
        bones=execSocket(self.inputs[1], context, data)
        if not bones:
            return None
        controller=execSocket(self.inputs[0], context, data)
        
        if not controller:
            return bones
        
        
        layers=[False]*32
        layers[controller["layer"]]=True
        
        def EDIT(armature):
            for ref in bones:
                p=ref.getEditBone()
                p.layers=layers
        
        def POSE(armature):
            for ref in bones:
                p=ref.getPoseBone()
                p.bone_group=controller["group"][1]
        
        objModeSession(bones.armature, 
        "EDIT", EDIT,
        "POSE", POSE)
        
        return bones