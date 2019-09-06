import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from .node.BoneNodeTree import updateTrees


class RigPP_OT_AddNodeCustomInput(bpy.types.Operator):
    bl_idname = "rigpp.add_node_custom_input"
    bl_label = "Add input"
    bl_description = "Add new custom node input"
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
        self.layout.prop(self.nuw,"type")
    
    def invoke(self, context, event):
        tree=self.getTree()
        caller=tree.nodes[self.caller]
        self.nuw=caller.customInputs.add()
        updateTrees(self, context)
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        return {"FINISHED"}
