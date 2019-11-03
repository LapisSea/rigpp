import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange
from ...BoneRef import (BoneRefList,BoneRef)

def growParents(chains,useStart,useEnd, careForConnected, ammount):
    infinite=ammount==-1
    ammountOrg=ammount
    
    for chain in chains:
        ammount=ammountOrg
        if useStart:
            while infinite or ammount>0:
                b=chain.base[0]
                
                if careForConnected and not b.use_connect:
                    break
                p=b.parent
                if not p:
                    break
                chain.base.insert(0,p)
                ammount-=1
                
        
        if useEnd:
            while infinite or ammount>0:
                last=chain.base[-1]
                fail=True
                for b in last.children:
                    if careForConnected and not b.use_connect:
                        continue
                    chain.base.append(b)
                    ammount-=1
                    fail=False
                    break
                if fail:
                    break
    
    return chains

def doGCON(chains,useStart,useEnd, ammount):
    return growParents(chains,useStart,useEnd, True,ammount)
def doGPAR(chains,useStart,useEnd, ammount):
    return growParents(chains,useStart,useEnd, False,ammount)
def doSHRI(chains,useStart,useEnd, leng):
    for chain in chains:
        while len(chain.base)>leng:
            if useEnd:
                del chain.base[-1]
            if useStart and len(chain.base)>leng:
                del chain.base[0]
    return chains

modificationTypes=[
    ("GCON", "Grow connected","Grows end of chain with parented bones that are connected"),
    ("GPAR", "Grow parented","Grows chain with parented bones"),
    ("SHRI", "Shrink","Shrinks to satisfy max size"),
]

modifiers={
    "GCON":doGCON,
    "GPAR":doGPAR,
    "SHRI":doSHRI,
}

class ModifyChain(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Modify chain'
    bl_icon = 'PLUS'
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketChain"],
            "default":"NodeSocketChain"
        }),
        ("MIRROR_TYPE", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    def onUpd(self,ctx):
        n="Growth limit"
        minim=-1
        if self.modType=="SHRI":
            n="To length"
            minim=1
        
        inp=self.inputs[3]
        inp.name=n
        inp.setRange(minim)
        valChange(self,ctx)
    
    modType: EnumProperty(items=modificationTypes, default=modificationTypes[0][0], update=onUpd)
    
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs .new('NodeSocketChainList', "Chains")
        self.inputs .new('NodeSocketBBool', "On start")
        self.inputs .new('NodeSocketBBool', "On end")
        self.inputs .new('NodeSocketBInt', "Limit").value=-1
        self.outputs.new('NodeSocketChainList', "Chains")
        self.onUpd(self,context)
        
        tree.endMultiChange()
        
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "modType", text="")
    #     layout.prop(self, "start")
    #     layout.prop(self, "end")
    #     if self.modType=="SHRI":
    #         layout.prop(self, "length")
    
    def execute(self,context, socket, data):
        single=socket.bl_idname=="NodeSocketChain"
        
        chains=execSocket(self.inputs[0], context, data)
        
        if not chains:
            return None if single else []
        
        length=execSocket(self.inputs[3], context, data)
        if length==0 or self.mute:
            return chains
        
        start=execSocket(self.inputs[1], context, data)
        end=execSocket(self.inputs[2], context, data)
        
        if not start and not end:
            return None if single else []
        
        if single:
            chains=[chains]
        
        armS=[c.base.armature for c in chains]
        
        for chain in chains:
            chain.base=chain.base.getBones()
        
        
        modifiers.get(self.modType)(chains, start, end, length)
        
        for (arm,chain) in zip(armS, chains):
            chain.base=BoneRefList.fromBones(arm,chain.base)
        
        if single:
            return chains[0]
        
        return chains