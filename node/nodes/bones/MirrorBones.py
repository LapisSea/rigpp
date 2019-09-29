import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

directions=[
    ("NEGATIVE_X", "-X",""),
    ("POSITIVE_X", "+X",""),
]

class MirrorBones(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Mirror Bones'
    bl_icon = 'PLUS'
    
    direction: EnumProperty(name="Direction", items=directions, update=valChange)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"direction",text="")
    
    def init(self, context):
        self.inputs.new('NodeSocketArmature', "Armature")
        self.inputs.new("NodeSocketBoneList", "Bones")
        self.outputs.new('NodeSocketArmature', "Armature")
    
    def execute(self,context, socket,tree):
        
        def doMirror(armature):
            eBones=armature.data.edit_bones
            
            for eBone in eBones:
                eBone.select=False
            
            for bone in bones:
                eb=eBones[bone[0]]
                eb.select=True
                eb.select_head =True
                eb.select_tail =True
            bpy.ops.armature.symmetrize(direction=self.direction)
        
        armature=self.inputs[0].execute(context,tree)
        if not armature:
            return None
        
        bones=execSocket(self.inputs[1], context, tree)
        if not bones:
            return armature
        
        objModeSession(armature,"EDIT", doMirror)
        
        return armature