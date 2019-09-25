import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone

class RigPP_OT_BClean(bpy.types.Operator):
    bl_idname = "rigpp.cleanup_b_names"
    bl_label = "Clean up bone names"
    bl_description = "Clean up bone names to fix the belnder standard (EG: Foo.001.L -> Foo.L.001)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return hasArmatureContext(context)

    def execute(self, context):
        count = 0
        for obj in getArmatures(context):
            armature: bpy.types.Armature = obj.data
            
            bones=armature.edit_bones if context.mode=="EDIT_ARMATURE" else armature.bones
            
            for bone in bones:
                name: str = bone.name
                oldName = bone.name

                segments = name.split(".")

                if len(segments) < 3:
                    continue

                change = True
                while change:
                    change = False
                    
                    
                    pos = -1
                    for pos in range(1, len(segments)):
                        if isDirection(segments[pos]):
                            
                            s = segments[pos-1]
                            if s.isnumeric() and s.startswith("0"):
                                segments.pop(pos-1)
                                change = True
                                break
                            
                            if pos+1<len(segments):
                                s = segments[pos+1]
                                
                                if s.isnumeric() and s.startswith("0"):
                                    segments.pop(pos+1)
                                    change = True
                                    break


                name = ".".join(segments)
                
                if name != oldName and name not in bones:
                    print(name, oldName)
                    bone.name = name
                    count += 1

        if count > 0:
            s = ""
            if count != 1:
                s = "s"
            self.report({'INFO'}, "Cleaned up "+str(count)+" bone name"+s+"!")
        
        return {"FINISHED"}
