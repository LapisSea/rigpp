import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

class ResolveChains(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Resolve chains'
    bl_icon = 'PLUS'
    
    def isTerminator(self):
        return True
    
    def init(self, context):
        self.inputs.new('NodeSocketArmature', "Armature")
        self.inputs.new('NodeSocketChainList', "Chains")
        self.outputs.new('NodeSocketArmature', "Armature")
    
    def execute(self,context, socket, data):
        
        armature=execSocket(self.inputs[0], context, data)
        if not armature:return armature
        
        chains=execSocket(self.inputs[1], context, data)
        if not chains:return armature
            
        tree=data["tree"]
        caches=data["run_cache"]
        
        if "groupCache" not in caches:
            caches["groupCache"]={}
        
        groupCache=caches["groupCache"]
        
        def getGroup(id):
            if id in groupCache:
                return groupCache[id]
                
            g=tree.findNode("ChainAttributeIn",lambda nod:nod.id==id)
            
            if not g:
                raise Exception(str(id))
            
            groupCache[id]=g
            return g
        
        d=data.copy()
        for chain in chains:
            
            for attrNode in chain.attributes:
                
                cache=[None] * (len(attrNode.inputs)-1)
                
                def getIn(pos):
                    if cache[pos]==None:
                        cache[pos]=execSocket(attrNode.inputs[pos+1], context, data)
                    
                    return cache[pos]
                
                group=getGroup(attrNode.getId())
                d["chain"]=chain
                d["armature"]=armature
                d["customInpGet"]=getIn
                group.runGroup(context, d)
        
        return armature
    