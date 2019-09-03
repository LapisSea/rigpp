import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone, PoseBone
from mathutils import Matrix, Vector, Euler
from mathutils.geometry import interpolate_bezier
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_SplineChain(bpy.types.Operator):
    bl_idname = "rigpp.parent_to_surface"
    bl_label = "Parent To Surface"
    bl_description = "Find closes vertex on active object from selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):

        if context.mode != "OBJECT":
            return False

        target = context.active_object
        if target is None or target.type != "MESH":
            return False

        mesh = target.data

        if len(mesh.vertices) < 1:
            return False

        if len(context.selected_objects) < 2:
            return False

        return True

    def execute(self, context):

        target = context.active_object
        mesh = target.data
        vertices = mesh.vertices
        
        orgId=[]
        
        for i,vt in enumerate(vertices):
            if vt.select:
                orgId.append(i)
                vt.select = False
        
        toParent=list(context.selected_objects)
        
        for obj in toParent:
            if obj == target:
                continue
            
            obj.select_set(False)
        
        
        for obj in toParent:
            if obj == target:
                continue

            location = obj.location

            def dist(id, pos): return (pos-vertices[id].co).length

            closest = 0
            closestDist = dist(closest, location)

            for i, vt in enumerate(vertices):
                if i == closest:
                    continue

                d = dist(closest, vt.co)

                if d<closestDist:
                    closestDist=d
                    closest=i
            
            vertices[closest].select=True
            
            obj.select_set(True)
            bpy.ops.object.parent_set(type='VERTEX')
            obj.select_set(False)
            
            vertices[closest].select=False
            

        for obj in toParent:
            if obj == target:
                continue
            
            obj.select_set(True)
        
        for id in orgId:
            vertices[id].select=True
        
        return {"FINISHED"}
