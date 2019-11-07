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
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketChainList"],
            "default":"NodeSocketChainList"
        }),
        ("MIRROR_TYPE", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    def isTerminator(self):
        return True
        
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketChainList', "Chains")
        self.outputs.new('NodeSocketChainList', "Chains")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket, data):
        
        chains=execSocket(self.inputs[0], context, data)
        if not chains:return None
            
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
        
        
        for chain in chains:
            
            for attrNode in chain.attributes:
                
                cache=[None] * (len(attrNode.inputs)-1)
                
                def getIn(pos):
                    if cache[pos]==None:
                        cache[pos]=execSocket(attrNode.inputs[pos+1], context, data)
                    
                    return cache[pos]
                
                groupId=attrNode.getId()
                group=getGroup(groupId)
                opCache={}
                
                data["run_cache"]["group_outputs"][groupId]=opCache
                d={**data, "chain":chain, "customInpGet": getIn}
                d["run_cache"]={"outputs":opCache}
                
                group.runGroup(context, d)
        
        
        return chains