import bpy
from . utils import *
from bpy.types import Armature, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *
from . constraint_mirror import makeMirrorConsrtaint


class RigPP_OT_SymConstraints(bpy.types.Operator):
    bl_idname = "rigpp.sym_constraints"
    bl_label = "Symmetrize Constraints"
    bl_description = "Similar to snap by symetry. Tries to find bones on opposite side of an axis and checks if their names match. (Foo.Top and Foo.Bot)"
    bl_options = {'REGISTER', 'UNDO'}

    class Dir():
        def __init__(self, id):
            axisId = id >> 1
            alter = id % 2 != 1
            filterFlip = 1 if alter else -1
            axisName = ["L", "Fr", "Top"][axisId]
            posNeg = ["positive", "negative"]

            if alter:
                axisName = reverseDirection(axisName)

            self.filter = lambda bone: findDirection(bone.name) != axisName
            self.tupple = (
                str(id),
                axisName+" To " + reverseDirection(axisName),
                "Mirror from "+axisName + " to "+reverseDirection(axisName)
            )

    directionMap = {}

    for i in range(6):
        directionMap[str(i)] = Dir(i)

    direction: EnumProperty(name="Direction",
                            default="0",
                            items=list(e.tupple for e in directionMap.values()))

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "direction")

    @classmethod
    def poll(self, context):
        if context.mode != "POSE":
            return False
        return hasArmatureContext(context)

    def execute(self, context):
        direction = self.directionMap[self.direction]

        filt = direction.filter

        count = 0
        for obj in getArmatures(context):

            bones = obj.pose.bones

            for bone in bones:

                dir = findDirection(bone.name)

                if dir is None:
                    continue

                if filt(bone):
                    continue

                mirrorName = tryMirrorName(bone.name)

                if mirrorName not in bones:
                    continue

                mirrorBone = bones[mirrorName]

                if not bone.bone.select and not mirrorBone.bone.select:
                    continue

                count += 1
                clear(mirrorBone.constraints)

                for constraint in bone.constraints:
                    makeMirrorConsrtaint(mirrorBone, constraint)
                
        if count > 0:
            self.report({'INFO'}, "Mirrored "+str(count) +
                        " bones constraints"+s(count)+"!")

        return {"FINISHED"}
