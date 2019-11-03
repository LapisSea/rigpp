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
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketArmature', "Armature")
        self.inputs.new("NodeSocketBoneList", "Bones")
        self.outputs.new('NodeSocketArmature', "Armature")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket,tree):
        
        armature=self.inputs[0].execute(context,tree)
        bones=execSocket(self.inputs[1], context, tree)
        
        if not armature:
            if not bones:
                return None
            armature=bones.armature
        
        if not bones:
            return armature
        
        def doMirror(armature):
            eBones=armature.data.edit_bones
            selected=[b for b in eBones if b.select]
            
            for eBone in selected:
                eBone.select=False
            
            toMirror=bones.getEditBones()
            
            for eb in toMirror:
                eb.select=True
                eb.select_head =True
                eb.select_tail =True
            
            bpy.ops.armature.symmetrize(direction=self.direction)
            
            for eb in toMirror:
                eb.select=False
                eb.select_head =False
                eb.select_tail =False
                
            for eBone in selected:
                eBone.select=True
        
        objModeSession(armature,"EDIT", doMirror)
        
        return armature