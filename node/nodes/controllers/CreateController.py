import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *
from ....utils import (makeName,objModeSession,boneLayerWhitelist)

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import valChange


class CreateController(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Create Controller'
    bl_icon = 'PLUS'
    
    ctrlName: StringProperty(name="Name", default="MyController")
    
    def init(self, context):
        tree=self.getTree()
        tree.startMultiChange()
        
        self.inputs.new('NodeSocketBoneGroup', "Group")
        self.inputs.new('NodeSocketBInt', "Layer")
        self.inputs.new('NodeSocketBStr', "Name").value="Controller name"
        
        self.outputs.new('NodeSocketController', "Controller")
        
        tree.endMultiChange()
        
        
    def execute(self,context, socket, data):
        group=execSocket(self.inputs[0], context, data)
        layer=execSocket(self.inputs[1], context, data)
        ctrlName=execSocket(self.inputs[2], context, data)
        
        
        # base=data["chain"].base
        
        # boneNames=[]
        
        # def addBones(armature):
            
        #     for bb in base:
        #         ebs=armature.data.edit_bones
        #         b=ebs[bb.name]
                
        #         bn=makeName(b.name,ctrlName)
        #         eb=ebs[bn] if bn in ebs else ebs.new(bn)
                
        #         parent=b.parent
                
        #         if parent:
        #             if not boneNames:
        #                 eb.parent=ebs[parent.name]
        #             else:
        #                 name=makeName(parent.name,ctrlName)
        #                 if name in ebs:
        #                     eb.parent=ebs[name]
        #                 else:
        #                     eb.parent=ebs[parent.name]
                
        #         eb.use_connect=b.use_connect
                
        #         eb.head=b.head
        #         eb.tail=b.tail
        #         eb.roll=b.roll
        #         eb.layers=boneLayerWhitelist(layer)
        #         eb.use_deform=False
                
        #         boneNames.append(eb.name)
            
        
        
        # def setUpBones(armature):
        #     pose=armature.pose
        #     pbs=pose.bones
            
        #     for name in boneNames:
        #         pb=pbs[name]
        #         pb.bone_group=group[1]
        
        # objModeSession(group[0],
        #     "EDIT", addBones,
        #     "POSE", setUpBones
        # )
        
        return {
            "name":self.ctrlName,
            "group":group,
            "layer":layer,
            # "controlBones":boneNames
        }