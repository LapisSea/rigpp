import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *


class RigPP_OT_EmptyChainAttributeResolve(bpy.types.Operator):
    bl_idname = "rigpp.execute_bone_tree"
    bl_label = "EXECUTE"
    bl_description = ""
    bl_options = {"REGISTER",'UNDO'}
    
    treeRef: StringProperty()
    
    def getTree(self):
        if not self.treeRef:
            return None
        return bpy.data.node_groups[self.treeRef]
        
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
