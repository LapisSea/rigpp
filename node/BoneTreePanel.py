import bpy
from ..utils import makeId
from .BoneNodeTree import (TREE_ID,valChange)
from ..import_properties import *

class BoneTreePanel(bpy.types.Panel):
    bl_idname = "RIGPP_TREE_PT_BONE"
    bl_label = "RigPP Node Tree"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    
    @classmethod
    def poll(cls, context):
        tree = cls.getTree()
        if tree is None: return False
        return tree.bl_idname == TREE_ID

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
        
    def draw(self, context):
        layout = self.layout
        tree=self.getTree()
        c = layout.column()
        c.scale_y = 1.6
        execOp = c.operator(makeId("execute_bone_tree"), icon = "PLAY")
        execOp.treeRef=tree.name
        layout.prop(tree, "autoExecute")
