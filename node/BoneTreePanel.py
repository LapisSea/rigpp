import bpy
from ..utils import (makeId, getTree)
from .BoneNodeTree import (TREE_ID,valChange)
from ..import_properties import *

class BoneTreePanel(bpy.types.Panel):
    bl_idname = "RIGPP_TREE_PT_BONE"
    bl_label = "RigPP Node Tree"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    
    @classmethod
    def poll(cls, context):
        tree = getTree(context)
        if tree is None: return False
        return tree.bl_idname == TREE_ID
        
    def draw(self, context):
        layout = self.layout
        tree=getTree(context)
        
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
        tree=getTree(context)
            
        off=0
        
        for obj in context.selected_objects:
            if obj.type!="ARMATURE":
                continue
            
            n=tree.newNode("GetArmature")
            n.value=obj
            n.location=tree.view_center
            n.location[0]-=n.width/2
            n.location[1]+=off
            off+=n.height
        
        return {"FINISHED"}


class RigPP_OT_ExecuteTree(bpy.types.Operator):
    bl_idname = "rigpp.execute_bone_tree"
    bl_label = "EXECUTE"
    bl_description = ""
    bl_options = {"REGISTER",'UNDO'}
    
        
    @classmethod
    def poll(self, context):
        try:
            return getTree(context)!=None
        except:
            return False

    def execute(self, context):
        tree=getTree(context)
        
        tree.execute(context)
        return {"FINISHED"}


class RigPP_OT_UpdateTree(bpy.types.Operator):
    bl_idname = "rigpp.update_bone_tree"
    bl_label = "UPDATE"
    bl_description = ""
    bl_options = {"REGISTER",'UNDO'}
    
        
    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        tree=context.space_data.edit_tree
        tree.update()
        return {"FINISHED"}