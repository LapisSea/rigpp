import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange


class GetBoneParent(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get bone parent'
    bl_icon = 'PLUS'
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBone"
        }),
        ("MIRROR_TYPE", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketBone', "Bone")
        self.outputs.new('NodeSocketBone', "Parent")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        bones=execSocket(self.inputs[0], context, data)
        if not bones:
            return None
        
        def getParent(bone):
            armature=bone[1]
            name=bone[0]
            bones=armature.data.bones
            if name not in bones:
                return None
            parent=bones[name].parent
            
            if not parent:
                return None
            
            return (parent.name, armature)
        
        if isinstance(bones, list):
            return [getParent(bone) for bone in bones]
        
        return getParent(bones)