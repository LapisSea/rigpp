import bpy

from . utils import *
from . import_properties import *

class RigPP_PT_Panel(bpy.types.Panel):
    bl_idname = "RIGPP_OPS_PT_PANEL"
    bl_label = "Chains"
    bl_category = "Rigging++"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.rigpp_settings
        
        ikfkChains=findCreatedChains(context)
        if not(not ikfkChains):
            layout.label(text="IK FK Chain")
            
            for o in ikfkChains:
                chain:IKFKChain=o
                
                layout.label(text="Name: "+chain.name)
                
                # grid=layout.grid_flow(row_major=False, columns=3,even_columns=False, even_rows=False, align=True)
                # bones=getRelevantBones(chain.obj, context)
                
                # for i in range(len(chain.deform())):
                #     grid.prop([bones[chain.deform()[i]],bones[chain.ik()[i]],bones[chain.fk()[i]]], "name", text="")
                
                