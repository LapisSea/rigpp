import bpy
from . utils import *
from bpy.types import Armature, Bone
from mathutils import Matrix, Vector, Euler
from . import_properties import *



class RigPP_OT_BNameBySym(bpy.types.Operator):
    bl_idname = "rigpp.cleanup_b_name_by_sym"
    bl_label = "Name bones by position"
    bl_description = "Similar to snap by symetry. Tries to find bones on opposite side of an axis and checks if their names match. (Foo.Top and Foo.Bot)"
    bl_options = {'REGISTER', 'UNDO'}

    class Dir():
        def __init__(self, id):
            axisId = id >> 1
            alter = id % 2 != 1
            filterFlip = 1 if alter else -1
            axisName = "XYZ"[axisId]
            posNeg = ["positive", "negative"]

            def bit(i): return 1 if (1 << axisId) & (1 << i) == 0 else -1

            self.mirror = Vector((bit(0), bit(1), bit(2)))
            self.filter = lambda pos: pos[axisId]*filterFlip < 0
            self.tupple = (
                str(id),
                str("+" if alter else "-")+axisName+" To " + str("" if not alter else "-")+axisName,
                "Mirror from "+posNeg[id % 2]+" "+axisName + " to "+posNeg[(id+1) % 2]+" "+axisName
            )

    directionMap = {}

    for i in range(6):
        directionMap[str(i)] = Dir(i)

    direction: EnumProperty(name="Direction",
                            default="0",
                            items=list(e.tupple for e in directionMap.values()))

    tolerance: FloatProperty(name="Tolerance",
                             description="Minimum difference in distance to opposite side bone",
                             default=0.05,
                             min=0.00001,
                             max=10,
                             step=0.01)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tolerance")
        row = layout.row()
        row.prop(self, "direction")

    @classmethod
    def poll(self, context):
        return hasArmatureContext(context)

    def execute(self, context):
        direction = self.directionMap[self.direction]

        mirror = direction.mirror
        filt = direction.filter
        tolerance = self.tolerance
        
        count = 0
        for obj in getArmatures(context):
            armature: Armature = obj.data

            bones: list
            editMode: bool

            if context.mode == "EDIT_ARMATURE":
                bones = armature.edit_bones
                editMode = True
            else:
                bones = armature.bones
                editMode = False
            
            def getTail(bone):
                if editMode:
                    return bone.tail
                else:
                    return bone.tail_local

            def getHead(bone):
                if editMode:
                    return bone.head
                else:
                    return bone.head_local

            def setTail(bone, vec: Vector):
                if editMode:
                    bone.tail = vec
                else:
                    bone.tail_local = vec

            def setHead(bone, vec: Vector):
                if editMode:
                    bone.head = vec
                else:
                    bone.head_local = vec

            for bone in bones:

                tail: Vector = getTail(bone)
                head: Vector = getHead(bone)

                if filt(tail):
                    continue

                tail = Vector((tail.x*mirror.x,
                               tail.y*mirror.y,
                               tail.z*mirror.z))
                head = Vector((head.x*mirror.x,
                               head.y*mirror.y,
                               head.z*mirror.z))

                dist = float("inf")
                bestBone = None

                for testBone in bones:
                    if bone == testBone:
                        continue

                    distNew = \
                        (tail-getTail(testBone)).length + \
                        (head-getHead(testBone)).length

                    if distNew < dist:
                        dist = distNew
                        bestBone = testBone

                if bestBone is not None and dist <= tolerance:
                    
                    if not bestBone.select and not bone.select:
                        continue
                    
                    modified = False

                    if getTail(bestBone) != tail:
                        modified = True
                        setTail(bestBone, tail)

                    if getHead(bestBone) != head:
                        modified = True
                        setHead(bestBone, head)

                    dir = findDirection(bone.name)
                    if dir is None:
                        if bestBone.name != bone.name:
                            modified = True
                            bestBone.name = bone.name
                    else:
                        reverse = reverseDirection(dir)
                        newName = None

                        if bone.name.endswith("."+dir):
                            newName = bone.name.replace("."+dir, "."+reverse)
                        else:
                            newName = bone.name.replace("."+dir+".", "."+reverse+".")

                        if bestBone.name != newName:
                            modified = True
                            bestBone.name = newName
                        
                    if modified:
                        count += 1

        if count > 0:
            self.report({'INFO'}, "Snapped "+str(count)+" bone name"+s(count)+"!")

        return {"FINISHED"}
