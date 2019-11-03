import bpy
import os
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from . bone_shapes import *
from .node.BoneNodeTree import updateTrees

from .node.sockets.types.SocketReference import (SocketReference,types)


class RigPP_OT_AddNodeCustomInput(bpy.types.Operator):
    bl_idname = makeId("add_node_custom_input")
    bl_label = "Add"
    bl_description = "Add new custom node input"
    bl_options = {'UNDO',"REGISTER","INTERNAL"}
    
    caller: StringProperty()
    
    def getTree(self):
        return bpy.context.space_data.edit_tree
    
    def getNode(self):
        return self.getTree().nodes[self.caller]
    
    @classmethod
    def poll(self, context):
        return True
    
    sockType: EnumProperty(name="Type", items=types)
    name: StringProperty(name="Name", default="")
    
    def draw(self, context):
        
        self.layout.label(text="Select custom input name and type")
        
        self.layout.prop(self,"name")
        self.layout.prop(self,"sockType")
        
        
    
    def invoke(self, context, event):
        self.sockType=types[0][0]
        self.name=""
        
        return context.window_manager.invoke_props_dialog(self)
        
    
    def execute(self, context):
        
        caller=self.getNode()
        
        new=caller.customInputs.add()
        new.sockType=self.sockType
        new.name=self.name
        
        
        return {"FINISHED"}


class RigPP_OT_RemoveNodeCustomInput(bpy.types.Operator):
    bl_idname = makeId("remove_node_custom_input")
    bl_label = "Remove"
    bl_description = "Remove new custom node input"
    bl_options = {'UNDO',"REGISTER","INTERNAL"}
    
    caller: StringProperty()
    
    def getTree(self):
        return bpy.context.space_data.edit_tree
    
    def getNode(self):
        return self.getTree().nodes[self.caller]
    
    @classmethod
    def poll(self, context):
        
        return True
    
    def makeOptions(self,context):
        caller=context.space_data.edit_tree.nodes[self.caller]
        
        return [(str(i), inp.name, "") for i, inp in enumerate(caller.customInputs)]
    
    option: EnumProperty(name="Option", items=makeOptions)
    
    def draw(self, context):
        
        self.layout.prop(self,"option", text="")
        
    
    def invoke(self, context, event):
        try:
            self.option="0"
        except:
            return {"CANCELLED"}
        
        return context.window_manager.invoke_props_dialog(self, width=200)
        
    
    def execute(self, context):
        
        tree=self.getTree()
        tree.startMultiChange()
        
        caller=self.getNode()
        
        caller.customInputs.remove(int(self.option))
        
        tree.endMultiChange()
        
        
        return {"FINISHED"}

actions=[
    RigPP_OT_AddNodeCustomInput,
    RigPP_OT_RemoveNodeCustomInput
]