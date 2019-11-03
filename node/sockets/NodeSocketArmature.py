import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ...import_properties import *
from bpy.types import Bone
from ...utils import (execNode,execSocket)

from .. import (BoneNodeSocket,BoneNodeSocketList)

class NodeSocketArmature(BoneNodeSocket):
    bl_idname = os.path.basename(__file__)[:-3]
    bl_label = 'Armature Node Socket'
    
    selfTerminator:BoolProperty()
    
    def armatureOnly(self, obj):
        return obj.type=="ARMATURE"
    
    value: PointerProperty(type=bpy.types.Object, poll=lambda self, obj:obj.type=="ARMATURE")
    
    def drawProp(self, layout, text):
        if self.value:
            layout.prop(self, "value", text="")
        else:
            layout.prop(self, "value", text=text)
    
    def draw_color(self, context, node):
        return (0.964706, 0.411765, 0.07451, 1)
    
    def getCastExplicit(self,target):
        if target.bl_idname==self.bl_idname+"List":
            return "MakeList"
        elif target.bl_idname=="NodeSocketBoneList":
            return "GetBones"
        else:
            return None