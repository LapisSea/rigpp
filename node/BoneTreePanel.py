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
        
        c.operator(makeId("execute_bone_tree"), icon = "PLAY")
        
        layout.prop(tree, "autoExecute")
        
        layout.operator(makeId("pick_armature"), icon = "EYEDROPPER")

class RigPP_OT_PickArmature(bpy.types.Operator):
    bl_idname = makeId("pick_armature")
    bl_label = "Pick selected armature(s)"
    bl_description = ""
    bl_options = {"REGISTER",'UNDO'}
    
    @classmethod
    def poll(self, context):
        for obj in context.selected_objects:
            if obj.type=="ARMATURE":
                return True
        return False

    def execute(self, context):
        tree=None
        try:
            tree=self.getTree()
        except:
            return {"FINISHED"}
            
        off=0
        
        for obj in context.selected_objects:
            if obj.type!="ARMATURE":
                continue
            
            n=tree.newNode("GetArmature")
            n.value=obj
            n.hide=True
            n.location=tree.view_center
            n.location[0]-=n.width/2
            n.location[1]+=off
            off+=n.height
        
        return {"FINISHED"}


class RigPP_OT_EmptyChainAttributeResolve(bpy.types.Operator):
    bl_idname = "rigpp.execute_bone_tree"
    bl_label = "EXECUTE"
    bl_description = ""
    bl_options = {"REGISTER",'UNDO'}
    
    
    def getTree(self):
        return bpy.context.space_data.edit_tree
        
    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        tree=None
        try:
            tree=self.getTree()
        except:
            return {"FINISHED"}
            
        
        tree.execute(context)
        return {"FINISHED"}
