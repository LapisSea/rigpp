import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ..import_properties import *
from bpy.types import Bone
from ..utils import (execNode,execSocket)

from .BoneNodeTree import valChange

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
        "selfTerminator":BoolProperty(),
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
        "selfTerminator":BoolProperty(),
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


def drawPropGhostText(self, layout, text):
    if self.value:
        layout.prop(self, "value", text="")
    else:
        layout.prop(self, "value", text=text)

def drawPropAlwaysText(self, layout, text):
    layout.prop(self, "value", text=text)

generate("Armature", (0.964706, 0.411765, 0.07451),
    getCastExplicit=lambda self, target: "GetBones" if target.bl_idname=="NodeSocketBoneList" else None,
    custom={
        "value": PointerProperty(type=bpy.types.Object, poll=lambda self, obj:obj.type=="ARMATURE"),
        "drawProp": drawPropGhostText
    }
)

generate("BBool", (178/256, 106/256, 48/256),
    custom={
        "value": BoolProperty(name="value", update=valChange),
        "drawProp": drawPropAlwaysText
    }
)


def drawPropColor(self, layout, text):
    if self.selfTerminator:
        l=layout.column()
        l.template_color_picker(self, "value",value_slider=True)
        l.prop(self, "value", text="")
    else:
        layout.prop(self, "value", text=text)

def getValColor(self):
    from .RGBA import RGBA
    return RGBA(self.value)

def executeColor(self,context, data):
    if self.selfTerminator:
        return self.getVal()
    
    if self.is_output:
        return execNode(self.node,self,context,data)
    
    links=self.links
    if not links:
        return self.getVal()
    
    return execSocket(links[0].from_socket, context,data)

generate("BColor", (199/256, 199/256, 41/256),
    custom={
        "value": FloatVectorProperty(name="value", subtype="COLOR",size=4, update=valChange,min=0, max=1, default=(1,1,1,1)),
        "drawProp": drawPropColor,
        "getVal": getValColor,
        "execute": executeColor
    }
)


def float_setRange(self,minVal=-2147483647,maxVal=2147483647):
    self.minVal=minVal
    self.maxVal=maxVal

def float_setval(self, val):
    new=min(self.maxVal, max(self.minVal,val))
    if new!=float_getval(self):
        self["value"]=new
        valChange(self,None)

def float_getval(self):
    return min(self.maxVal, max(self.minVal,self.get("value",0)))

generate("BFloat", (161/256, 161/256, 161/256),
    custom={
        "setRange": float_setRange,
        "minVal": FloatProperty(default=-2147483647),
        "maxVal": FloatProperty(default=2147483647),
        "value": FloatProperty(name="value", set=float_setval, get=float_getval),
        "drawProp": drawPropAlwaysText,
    }
)


def int_setRange(self,minVal=-2147483647,maxVal=2147483647):
    self.minVal=minVal
    self.maxVal=maxVal

def int_setval(self, val):
    new=min(self.maxVal, max(self.minVal,val))
    if new!=int_getval(self):
        self["value"]=new
        valChange(self,None)

def int_getval(self):
    return min(self.maxVal, max(self.minVal,self.get("value",0)))

generate("BInt", (15/256, 133/256, 38/256),
    canCast=lambda self, socket: socket.bl_idname=="NodeSocketBFloat",
    custom={
        "setRange": int_setRange,
        "minVal": IntProperty(default=-2147483647),
        "maxVal": IntProperty(default=2147483647),
        "value": IntProperty(name="value", set=int_setval, get=int_getval),
        "drawProp": drawPropAlwaysText,
    }
)


generate("BMatrix", (0.4, 0.6, 1))

generate("BoneGroup", (1, 0, 0.5))

from .BoneRef import (BoneRefList,BoneRef)

generate("Bone", (0.4, 1, 1),
    getCastExplicit=lambda self, target: "MakeChains" if target.bl_idname=="NodeSocketChainList" else None,
    customList={
        "getValue": lambda self: BoneRefList([])
    }
)

def drawPropTerminNoText(self, layout, text):
    if self.selfTerminator:
        layout.prop(self, "value", text="")
    else:
        layout.prop(self, "value", text=text)

generate("BStr", (99/256, 99/256, 199/256),
    custom={
        "value": StringProperty(name="value", update=valChange, options={"TEXTEDIT_UPDATE"}),
        "drawProp":drawPropTerminNoText
    }
)


def drawPropVector(self, layout, text):
    g=layout.column(align=True)
    g.prop(self, "value", index=0, text="X")
    g.prop(self, "value", index=1, text="Y")
    g.prop(self, "value", index=2, text="Z")


generate("BVector", (99/256, 139/256, 250/256),
    custom={
        "value": FloatVectorProperty(name="value", subtype="XYZ", update=valChange),
        "drawProp":drawPropVector
    }
)

generate("Chain", (0.1, 0.3, 1),
    getCastExplicit=lambda self, target: "GetChainBase" if target.bl_idname=="NodeSocketBoneList" else None,
)


generate("Constraint", (0.104418, 1, 0.361321))

generate("Controller", (0.4, 1, 0.5))

generate("BObject", (1, 1, 0),
    custom={
        "value": PointerProperty(type=bpy.types.Object),
        "drawProp": drawPropGhostText
    }
)


