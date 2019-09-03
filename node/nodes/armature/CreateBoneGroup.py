import bpy
import os

from ... import BoneNode
from ....utils import makeId
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

colors=[
    ("0","DEFAULT", ""),
    ("1","THEME01", ""),
    ("2","THEME02", ""),
    ("3","THEME03", ""),
    ("4","THEME04", ""),
    ("5","THEME05", ""),
    ("6","THEME06", ""),
    ("7","THEME07", ""),
    ("8","THEME08", ""),
    ("9","THEME09", ""),
    ("10","THEME10", ""),
    ("11","THEME11", ""),
    ("12","THEME12", ""),
    ("13","THEME13", ""),
    ("14","THEME14", ""),
    ("15","THEME15", ""),
    ("16","THEME16", ""),
    ("17","THEME17", ""),
    ("18","THEME18", ""),
    ("19","THEME19", ""),
    ("20","THEME20", ""),
]

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
    
    groupName: StringProperty(name="Name", default="MyGroup", update=valChange)
    coloredConstraints: BoolProperty(name="Colored Constraints", default=False, update=valChange)
    customColors: BoolProperty(name="Custom colors", default=False, update=setChanged)
    colorSet: EnumProperty(name="Color set", items=colors, update=setChanged)
    
    activeCol: FloatVectorProperty(subtype="COLOR",size = 3,min=0, max=1, default=(0.8,0.8,0.8), update=valChange)
    normalCol: FloatVectorProperty(subtype="COLOR",size = 3,min=0, max=1, default=(0.8,0.8,0.8), update=valChange)
    selectCol: FloatVectorProperty(subtype="COLOR",size = 3,min=0, max=1, default=(0.8,0.8,0.8), update=valChange)
    
    def init(self, context):
        self.outputs.new('NodeSocketBoneGroup', "Group")
        self.setColors(context,1)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "groupName", text="")
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
        groups=data["armature"].pose.bone_groups
        if self.groupName in groups:
            group=groups[self.groupName]
        else:
            group=groups.new(name=self.groupName)
        
        if not self.customColors:
            group.color_set=colors[int(self.colorSet)][1]
            return group
        
        group.color_set="CUSTOM"
        col=group.colors
        col.active=self.activeCol
        col.normal=self.normalCol
        col.select=self.selectCol
        col.show_colored_constraints=self.coloredConstraints
        
        return group