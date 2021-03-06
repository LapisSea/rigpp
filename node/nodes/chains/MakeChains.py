import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execNode,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter

from ...BoneChain import BoneChain
from ...BoneNodeTree import valChange
from ...BoneRef import (BoneRefList,BoneRef)

def doParents(bones,connectedDontCare):
    result=[]
    while bones:
        
        chain=BoneChain()
        chain.base.append(bones.pop())
        change=True
        while change:
            change=False
            for bone in bones:
                if chain.base[-1]==bone.parent:
                    chain.base.append(bone)
                    bones.remove(bone)
                    change=True
                    break
                if chain.base[0].parent==bone:
                    chain.base.insert(0,bone)
                    bones.remove(bone)
                    change=True
                    break
        result.append(chain)
    
    return result

def doCONP(bones):
    return doParents(bones,False)
def doPARE(bones):
    return doParents(bones,True)

def doNUMN(bones):
    result=[]
    while bones:
        
        chain=BoneChain()
        result.append(chain)
        
        segments=bones[0].name.split(".")
        try:
            int(segments[-1])
            segments.remove(-1)
        except:
            pass
        
        import re
        
        pattern = re.compile("\\.".join(segments)+"(\\.[0-9]+)?")
        
        for bone in bones:
            if pattern.match(bone.name):
                chain.base.append(bone)
        
        for added in chain.base:
            bones.remove(added)
        
        def byName(bone):
            return bone.name
        chain.base.sort(key=byName)
    
    return result

constructionTypes=[
    ("CONP","Connected parents", "Creates chains from set of bones that are parented and connected"),
    ("PARE","Parents", "Creates chains from set of bones that are parented"),
    ("NUMN","Numbered names", "Creates chains from set of bones that have the same names (Ignoring the ending dot and number)"),
]
constructioneers={
    "CONP":doCONP,
    "PARE":doPARE,
    "NUMN":doNUMN,
}
class MakeChains(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Make chains'
    bl_icon = 'PLUS'
    
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBoneList"
        }),
        ("MIRROR_IS_LIST", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    constructionType: EnumProperty(name="Construction Type",items=constructionTypes, default=constructionTypes[0][0], update=valChange)
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketBoneList", "Bones")
        self.outputs.new('NodeSocketChainList', "Chains")
        
        tree.endMultiChange()
        
    
    def draw_buttons(self, context, layout):
        if self.inputs[0].bl_idname.endswith("List"):
            layout.prop(self,"constructionType", text="")
    
    def execute(self,context, socket, data):
        bones=execSocket(self.inputs[0], context, data)
        if not bones:
            return bones
        
        if isinstance(bones, BoneRef):
            chain=BoneChain()
            chain.base=BoneRefList([bones])
            return chain
        
        chains=constructioneers.get(self.constructionType)(bones.getBones())
        
        for chain in chains:
            chain.base=BoneRefList.fromBones(bones.armature, chain.base)
        
        return chains
    
    def draw_label(self):
        if self.inputs[0].bl_idname.endswith("List"):
            return self.bl_label
        else:
            return "Make chain"