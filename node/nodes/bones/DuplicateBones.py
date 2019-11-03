import bpy
import os

from ... import BoneNode
from ....utils import (makeId,objModeSession,execSocket,boneLayerWhitelist)
from ....import_properties import *
from ...BoneNodeTree import valChange

from ...sockets.types.NameFilter import NameFilter

from ....name_deriver import name_deriver
from ...BoneRef import (BoneRefList,BoneRef)

class DuplicateBones(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Duplicate Bones'
    bl_icon = 'PLUS'
    
    def nameTypeChange(self, context):
        
        self.inputs[1].enabled=self.nameDerivation!="ANUM"
        
        valChange(self, context)
    
    nameDerivation: EnumProperty(items=name_deriver.types, description="How to generate new bone name", update=nameTypeChange, default="ADDP")
    nameValue: StringProperty(update=valChange)
    full: BoolProperty(update=valChange, name="Full copy")
    
    rules=[
        ("ADDAPTIVE_SOCKET", {
            "target":("input",0),
            "list_agnostic": True, 
            "accepted_types":["NodeSocketBone"],
            "default":"NodeSocketBone"
        }),
        ("MIRROR_TYPE", {
            "from": ("input",0),
            "to": ("output",0)
        }),
    ]
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketBone', "Bones to dup")
        self.inputs.new('NodeSocketBStr', "Bone name value")
        self.outputs.new('NodeSocketBone', "New bones")
        
        tree.endMultiChange()
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"nameDerivation", text="")
        layout.prop(self,"full")
        
    
    def execute(self,context, socket,tree):
        bones=execSocket(self.inputs[0], context, tree)
        if not bones:
            return None
        
        nameVal=None
        namTyp=self.nameDerivation
        
        if namTyp!="ANUM":
            nameVal=execSocket(self.inputs[1], context, tree)
        
        dupMapping={}
        
        def dup(ref):
            newName=name_deriver.derive(namTyp, ref.name, nameVal)
            
            if self.full:
                
                print(bpy.ops.armature.duplicate({}))
                
            else:
                ebs=bones.armature.data.edit_bones
                
                b=ref.getEditBone()
                
                eb=ebs.new(newName)
                dupMapping[ref.name]=eb.name
                
                parent=b.parent
                
                if parent.name in dupMapping.keys():
                    parent=ebs[dupMapping[parent.name]]
                
                eb.parent=parent
                eb.use_connect=b.use_connect
                
                eb.head=b.head
                eb.tail=b.tail
                eb.roll=b.roll
                eb.layers=b.layers
                eb.use_deform=b.use_deform
                
                return eb
        
        def do(armature):
            return BoneRefList.fromBones(bones.armature, [dup(ref) for ref in bones])
        
        return objModeSession(bones.armature,"EDIT",do)