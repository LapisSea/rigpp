import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket,objModeSession)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange
from ...BoneRef import (BoneRefList,BoneRef)


class AddBoneConstraint(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Add Bone Constraint'
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
        self.inputs.new('NodeSocketConstraint', "Constraint")
        self.outputs.new('NodeSocketBone', "Parent")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        bones=execSocket(self.inputs[0], context, data)
        if not bones:
            return None
            
        constraint=execSocket(self.inputs[1], context, data)
        if not constraint:
            return bones
        
        def do(armature):
            
            for bone in bones:
                pBone=bone.getPoseBone()
                
                new=pBone.constraints.new(constraint.name)
                constraint.applyAttributes(new)
                
        
        objModeSession(bones.armature,"POSE",do)
        
        return bones