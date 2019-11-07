import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,runLater,onDepsgraph,offDepsgraph)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter
from ...BoneRef import (BoneRefList,BoneRef)

from ....data_scrape import editBoneAttrs

class GetBoneAttribute(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Get bone attribute'
    bl_icon = 'PLUS'
    
    def getAttribType(self):
        return editBoneAttrs["types"][self.attr]
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBone"
        }),
        ("ADDAPTIVE_SOCKET", {
            "target":("output",0),
            "list_agnostic": True, 
            "accepted_types":lambda self:[self.getAttribType()],
            "default": getAttribType
        }),
        ("MIRROR_IS_LIST", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    def attrChange(self,ctx):
        print(self.getAttribType())
        valChange(self,ctx)
    
    attr: EnumProperty(items=lambda s,c: editBoneAttrs["enums"], name="Attribute", update=attrChange)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"attr",text="")
    
    def init(self, context):
        
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new("NodeSocketBone", "Bones")
        self.outputs.new("NodeSocketAny", "Value")
        
        tree.endMultiChange()
        
    
    def execute(self,context, socket,data):
        
        bones=execSocket(self.inputs[0], context, data)
        
        
        single=not socket.bl_idname.endswith("List")
        if not bones:
            return None if single else []
        
        data=[]
        
        def do(armature):
            for bone in bones:
                if bone:
                    eb=bone.getEditBone()
                    import copy
                    data.append(copy.deepcopy(getattr(eb,self.attr)))
        
        objModeSession(bones.armature,"EDIT",do)
        
        
        if single:
            return data[0]
        return data