import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)

class MakeList(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Make List'
    bl_icon = 'PLUS'
    
    def resize(self,tree):
        
        if not self.inputs:
            self.inputs.new("NodeSocketAny", "Any")
        
        if self.inputs[0].bl_idname=="NodeSocketAny":
            return
        
        for inp in self.inputs:
            
            if inp.bl_idname!="NodeSocketAny" and not inp.links:
                self.inputs.remove(inp)
        
        if self.inputs[-1].bl_idname!="NodeSocketAny":
            self.inputs.new("NodeSocketAny", "Any")
        
        if len(self.inputs)==1 and self.outputs[0].bl_idname!="NodeSocketAnyList":
            self.setIOType(self.outputs,0,"NodeSocketAnyList")
    
    
    def update(self):
        tree=self.getTree()
        
        if self.outputs[0].bl_idname=="NodeSocketAnyList":
            links=self.outputs[0].links
            if links:
                typ=links[0].to_socket.bl_idname
                if typ.endswith("List"):
                    self.setIOType(self.outputs,0,typ)
        
        for i in range(len(self.inputs)):
            inp=self.inputs[i]
            
            if inp.bl_idname=="NodeSocketAny":
                links=inp.links
                if not links:
                    continue
                
                targetTyp="NodeSocketAny"
                isOutAny=self.outputs[0].bl_idname=="NodeSocketAnyList"
                
                for link in links:
                    
                    socket=link.from_socket
                    
                    typ=socket.bl_idname
                    
                    if not isOutAny:
                        compare=typ if typ.endswith("List") else typ+"List"
                        if compare!=self.outputs[0].bl_idname:
                            self.getTree().links.remove(link)
                            break
                    
                    targetTyp=typ
                    break
                
                if targetTyp=="NodeSocketAny":
                    inp.name="Any"
                else:
                    inp.name="List" if targetTyp.endswith("List") else "Element"
                
                self.setIOType(self.inputs,i,targetTyp)
                
                if isOutAny:
                    self.setIOType(self.outputs,0,typ if typ.endswith("List") else typ+"List")
        
        if not self.keepDups:
            
            links=[]
            for inp in self.inputs:
                l=inp.links
                if not l:
                    continue
                
                sock=l[0].from_socket
                if sock in links:
                    tree.links.remove(l[0])
                    bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text="Duplicate input!"), title='Error', icon='ERROR')
                else:
                    links.append(sock)
        
        self.resize(tree)
    
    keepDups: BoolProperty(name="Keep duplicates", default=True, update=updateTrees)
        
    def init(self, context):
        self.inputs.new("NodeSocketAny", "Any")
        self.outputs.new("NodeSocketAnyList", "List")
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"keepDups")
    
    def execute(self,context, socket, data):
        result=[]
        def add(e):
            if self.keepDups:
                result.append(e)
            else:
                if e not in result:
                    result.append(e)
        
        for input in self.inputs:
            
            if not input.is_linked:
                continue
            
            res=execSocket(input, context, data)
            
            if isinstance(res, list):
                for e in res:
                    add(e)
            else:
                add(res)
        
        return result