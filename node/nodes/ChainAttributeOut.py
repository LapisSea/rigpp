import bpy
import os

from .. import BoneNode
from ...utils import (makeId,execSocket)
from ...import_properties import *

from ..sockets.types.NameFilter import NameFilter
from ..BoneNodeTree import updateTrees

class ChainAttributeOut(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get armature bones'
    bl_icon = 'PLUS'
    
    def groupMarkers(self):
        return ("END","REFERENCE")
    
    def getGroupId(self):
        return self.id
    
    id: IntProperty(default=-1, update=updateTrees)
    
    def init(self, context):
        self.inputs.new('NodeSocketBoneList', "New bones")
        self.inputs.new('NodeSocketControllerList', "Controllers")
    
    def update(self):
        tree=self.getTree()
        if self.id==-1:
            return
        
        for dup in tree.nodesByType("ChainAttributeOut"):
            if dup!=self and dup.id==self.id:
                tree.nodes.remove(self)
                return
        
        so=tree.findNode("ChainAttributeIn",lambda nod:nod.id==self.id)
        
        if not so:
            tree.nodes.remove(self)
            return
        
        self.label=so.attrName
        
    def runGroup(self,context, data):
        
        # controllers=execSocket(self.inputs[1], context, data)
        
        return [execSocket(inp, context, data) for inp in self.inputs]