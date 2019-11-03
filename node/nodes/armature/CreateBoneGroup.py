import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

colors=[("0","DEFAULT", "")]+[(str(i), "THEME"+str(i).zfill(2), "") for i in range(1, 21)]

class CreateBoneGroup(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Create Bone Group'
    bl_icon = 'PLUS'
    bl_width_default=160
    
    def setColors(self,ctx,id):
        
        
        colors=ctx.preferences.themes["Default"].bone_color_sets[id]
        self.activeCol=colors.active
        self.normalCol=colors.normal
        self.selectCol=colors.select
    
    def setChanged(self,ctx):
        if self.colorSet!="0":
            self.setColors(ctx,int(self.colorSet)-1)
        valChange(self,ctx)
    
    coloredConstraints: BoolProperty(name="Colored Constraints", default=False, update=valChange)
    customColors: BoolProperty(name="Custom colors", default=False, update=setChanged)
    colorSet: EnumProperty(name="Color set", items=colors, update=setChanged)
    
    activeCol: FloatVectorProperty(subtype="COLOR",size = 3,min=0, max=1, default=(0.8,0.8,0.8), update=valChange)
    normalCol: FloatVectorProperty(subtype="COLOR",size = 3,min=0, max=1, default=(0.8,0.8,0.8), update=valChange)
    selectCol: FloatVectorProperty(subtype="COLOR",size = 3,min=0, max=1, default=(0.8,0.8,0.8), update=valChange)
    
    def init(self, context):
        self.inputs.new('NodeSocketBStr', "Name").value="My Bone Group"
        self.inputs.new('NodeSocketArmature', "Armature")
        self.outputs.new('NodeSocketBoneGroup', "Group")
        self.setColors(context,1)
    
    def draw_buttons(self, context, layout):
        # layout.prop(self, "groupName", text="")
        layout.prop(self, "coloredConstraints")
        layout.prop(self, "customColors")
        
        if not self.customColors:
            layout.prop(self, "colorSet", text="")
            if self.colorSet!="0":
                c=layout.grid_flow(columns=3, even_columns=True,align=True,row_major=True)
                c.enabled = False
                c.prop(self, "normalCol",text="")
                c.prop(self, "selectCol",text="")
                c.prop(self, "activeCol",text="")
        else:
            c=layout.grid_flow(columns=3, even_columns=True,align=True,row_major=True)
            c.label(text="Normal")
            c.label(text="Select")
            c.label(text="Active")
            c.prop(self, "normalCol",text="")
            c.prop(self, "selectCol",text="")
            c.prop(self, "activeCol",text="")
    
    def execute(self,context, socket, data):
        group=None
        groupName=execSocket(self.inputs[0], context, data)
        armature=execSocket(self.inputs[1], context, data)
        
        groups=armature.pose.bone_groups
        
        if groupName in groups:
            group=groups[groupName]
        else:
            group=groups.new(name=groupName)
        
        if self.customColors:
            group.color_set="CUSTOM"
            col=group.colors
            col.active=self.activeCol
            col.normal=self.normalCol
            col.select=self.selectCol
            col.show_colored_constraints=self.coloredConstraints
        else:
            group.color_set=colors[int(self.colorSet)][1]
        
        return (armature, group) 