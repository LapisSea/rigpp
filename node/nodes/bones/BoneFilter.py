import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execNode)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange

class BoneFilter(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Filter bones'
    bl_icon = 'PLUS'
    bl_width_default=175
    
    filters: CollectionProperty(type=NameFilter, name="filters")
    
    
    def update(self):
        self.resize()
    
    def resize(self):
        if len(self.filters)==0 or len(self.filters[-1].value)>0:
            self.filters.add()
        
        for i in range(len(self.filters)-1):
            f=self.filters[i]
            if f.value=="":
                self.filters.remove(i)
                self.resize()
                break
    
    def init(self, context):
        self.inputs.new("NodeSocketBoneList", "Bones")
        self.outputs.new('NodeSocketBoneList', "Match Bones")
        self.outputs.new('NodeSocketBoneList', "Fail Bones")
        self.resize()
    
    def copy(self, node):
        self.resize()
    
    def draw_buttons(self, context, layout):
        
        for filter in self.filters:
            c=layout.grid_flow(columns=2, align=True)
            c.prop(filter, 'type',text="")
            c.prop(filter, 'value',text="", expand=True)
        
        layout.separator()
    
    def draw_label(self):
        if self.hide:
            if self.value=="":
                return "<VALUE EMPTY>"
            else:
                return ".?"+self.value+".?"
        else:
            return self.bl_label
    
    def execute(self,context, socket, data):
        
        match=socket==self.outputs[0]
        caches=data["run_cache"]
        
        if self.name not in caches:
            
            def check(name):
                for f in self.filters:
                    if not f.filter(name):
                        return False
                return True
            
            bones=execNode(self.inputs[0], context, data)
            cache={
                True:[],
                False:[]
            }
            caches[self.name]=cache
            
            
            for b in bones:
                cache[check(b.name)].append(b)
            
        
        return caches[self.name][match]