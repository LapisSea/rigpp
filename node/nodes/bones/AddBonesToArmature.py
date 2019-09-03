import bpy
import os

from ... import BoneNode
from ....utils import makeId
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

class AddBonesToArmature(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Add bones to armature'
    bl_icon = 'PLUS'
    
    keepDups: BoolProperty(name="Keep duplicates", default=False, update=valChange)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"keepDups")
        
    def init(self, context):
        self.inputs.new('NodeSocketArmature', "Armature")
        self.inputs.new("NodeSocketBoneList", "Bones")
        self.outputs.new('NodeSocketArmature', "Armature")
    
    def execute(self,context, socket,tree):
        armature=self.inputs[0].execute(context,tree)
        bones=self.inputs[1].execute(context,tree)
        
        print("TODO: AddBonesToArmature implement bone adding")
        
        return armature