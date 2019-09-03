import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execNode)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

def growParents(chains,useStart,useEnd, careForConnected):
    
    for chain in chains:
        if useStart:
            while True:
                b=chain.base[0]
                
                if careForConnected and b.use_connect:
                    break
                p=b.parent
                if not p:
                    break
                chain.base.insert(0,p)
        
        if useEnd:
            while True:
                last=chain.base[-1]
                fail=True
                for b in last.children:
                    if careForConnected and not b.use_connect:
                        continue
                    chain.base.append(b)
                    fail=False
                    break
                if fail:
                    break
    
    return chains

def doGCON(chains,useStart,useEnd, len):
    return growParents(chains,useStart,useEnd, True)
def doGPAR(chains,useStart,useEnd, len):
    return growParents(chains,useStart,useEnd, False)
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
    
    modType: EnumProperty(items=modificationTypes, default=modificationTypes[0][0], update=valChange)
    start:BoolProperty(name="On start", update=valChange)
    end:BoolProperty(name="On end", update=valChange)
    length:IntProperty(name="Target Length", default=2, min=1, update=valChange)
    
    def init(self, context):
        self.inputs .new('NodeSocketChainList', "Chains")
        self.outputs.new('NodeSocketChainList', "Chains")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "modType", text="")
        layout.prop(self, "start")
        layout.prop(self, "end")
        if self.modType=="SHRI":
            layout.prop(self, "length")
    
    def execute(self,context, socket, data):
        chains=execNode(self.inputs[0], context, data)
        
        m=modifiers.get(self.modType)(chains, self.start, self.end, self.length)
        
        return chains