import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_EmptyChainAttributeResolve(bpy.types.Operator):
    bl_idname = "rigpp.empty_chain_attribute_resolve"
    bl_label = "Add new definition"
    bl_description = ""
    bl_options = {'UNDO',"INTERNAL"}
    
    x:FloatProperty()
    y:FloatProperty()
    
    caller: StringProperty()
    
    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        bpy.ops.node.select_all(action='DESELECT')
        
        tree=getTree()
        n=tree.newNode("ChainAttributeIn")
        
        caller=tree.nodes[self.caller]
        caller.attribute=str(n.id)
        
        bpy.ops.transform.translate(value=(self.x,self.y,0))
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        return {"FINISHED"}
