import bpy
import os

from .. import BoneNode
from ...utils import (makeId,execNode)
from ...import_properties import *

from ..sockets.types.NameFilter import NameFilter
from ..BoneNodeTree import updateTrees

class ChainAttributeOut(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get armature bones'
    bl_icon = 'PLUS'
    
    id: IntProperty(default=-1, update=updateTrees)
    
    def init(self, context):
        self.inputs.new('NodeSocketBoneList', "New bones")
        self.inputs.new('NodeSocketControllerList', "Controllers")
    
    def treeUpdate(self,tree):
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
        
        self.use_custom_color=so.use_custom_color
        self.color=so.color
        self.label=so.attrName
        
    def runGroup(self,context, data):
        controllers=execNode(self.inputs[1], context, data)
        
        # print("ay",controllers)