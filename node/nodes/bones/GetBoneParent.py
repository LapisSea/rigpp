import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange
from ...BoneRef import (BoneRefList,BoneRef)


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
            bon=bone.getBone()
            if not bon:
                return None
            
            parent=bon.parent
            
            if not parent:
                return None
            
            return BoneRef(bone.armature, parent.name)
        
        if isinstance(bones, BoneRefList):
            
            return BoneRefList([getParent(bone) for bone in bones.refs])
        
        return getParent(bones)