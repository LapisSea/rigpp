import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ..import_properties import *
from bpy.types import Bone
from ..utils import (execNode,execSocket)

generated_classes=[]

def generate(
name,
color,
canCast=lambda self, socket: False,
getCastExplicit=lambda self, target: None,
canCastList=lambda self, socket: False,
getCastListExplicit=lambda self, target: None,
custom={},
customList={}
):
    from . import (BoneNodeSocket,BoneNodeSocketList)
    
    name = "NodeSocket"+name
    
    boneColor = (*color, 1)
    
    def bone_getCastExplicit(self, target):
        if target.bl_idname == self.bl_idname+"List":
            return "MakeList"
        else:
            getCastExplicit()
    
    boneType=type(name, (BoneNodeSocket,), {
        "bl_idname": name,
        "bl_label": name+' Socket',
        "draw_color": lambda self, context, node: boneColor,
        "canCast": canCast,
        getCastExplicit: bone_getCastExplicit,
        **custom
    })
    
    listName = name+"List"
    boneListColor = (*color, 0.5)
    
    boneListType=type(listName, (BoneNodeSocket,), {
        "bl_idname": listName,
        "bl_label": listName+' Socket',
        "draw_color": lambda self, context, node: boneListColor,
        "canCast": canCastList,
        getCastExplicit: getCastListExplicit,
        **customList
    })
    
    generated_classes.append(boneType)
    generated_classes.append(boneListType)

generate("Any", (0.5, 0.5, 0.5),
canCast=lambda self, socket: True,
canCastList=lambda self, socket: socket.bl_idname.endswith("List"),
)
