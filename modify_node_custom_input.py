import bpy
import os
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from . bone_shapes import *
from .node.BoneNodeTree import updateTrees

from .node.sockets.types.SocketReference import SocketReference

class RigPP_OT_AddNodeCustomInput(bpy.types.Operator):
    bl_idname = makeId("add_node_custom_input")
    bl_label = "Add"
    bl_description = "Add new custom node input"
    bl_options = {'UNDO',"REGISTER","INTERNAL"}
    
    treeRef: StringProperty()
    caller: StringProperty()
    doExec: BoolProperty(default=False)
    
    new: PointerProperty(type=SocketReference)
    
    def getTree(self):
        return bpy.data.node_groups[self.treeRef]
    
    @classmethod
    def poll(self, context):
        return True
    
    def draw(self, context):
        
        self.layout.label(text="Select custom input name and type")
        
        self.layout.prop(self.new,"name")
        self.layout.prop(self.new,"sockType")
        
        ok=self.layout.operator(self.bl_idname,text="Confirm")
        ok.doExec=True
        
        ok.new.name=self.new.name
        ok.new.sockType=self.new.sockType
    
    def invoke(self, context, event):
        if not self.doExec:
            return context.window_manager.invoke_props_popup(self, event)
        return {"FINISHED"}

    def execute(self, context):
        if self.doExec:
            tree=self.getTree()
            caller=tree.nodes[self.caller]
            
            updateTrees(self, context)
            return {"FINISHED"}
        
        return {"CANCELLED"}

class RigPP_OT_RemoveNodeCustomInput(bpy.types.Operator):
    bl_idname = makeId("remove_node_custom_input")
    bl_label = "Remove"
    bl_description = "Remove new custom node input"
    bl_options = {'UNDO',"REGISTER","INTERNAL"}
    
    treeRef: StringProperty()
    caller: StringProperty()
    
    def getTree(self):
        return bpy.data.node_groups[self.treeRef]
    
    @classmethod
    def poll(self, context):
        return True
    
    def draw(self, context):
        
        self.layout.label(text="Select custom input name and type")
        self.layout.prop(self.nuw,"name")
        self.layout.prop(self.nuw,"sockType")
        
    
    def invoke(self, context, event):
        tree=self.getTree()
        caller=tree.nodes[self.caller]
        
        self.nuw=caller.customInputs.add()
        updateTrees(self, context)
        
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        return {"FINISHED"}

actions=[
    RigPP_OT_AddNodeCustomInput,
    RigPP_OT_RemoveNodeCustomInput
]