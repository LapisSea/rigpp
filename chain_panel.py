import bpy

class RigPP_PT_Panel(bpy.types.Panel):
    bl_idname = "RIGPP_CHAIN_PT_PANEL"
    bl_label = "Rigging++"
    bl_category = "Rigging++"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.rigpp_settings
        
        def op(name:str):
            row = layout.row()
            row.operator("rigpp."+name)
        
        op("cleanup_b_names")
        op("cleanup_b_name_by_sym")
        row = layout.row()
        op("create_ik_fk_chain")
        op("ik_fk_bone_control")
        op("ik_fk_bone_control_invert")
        row = layout.row()
        op("create_spline_chain")
        row = layout.row()
        op("parent_to_surface_tri")
        op("parent_to_surface")
        op("parent_to_closest_bone")
        op("copy_transforms")
        op("copy_rotation")
        op("sym_constraints")
        