import bpy
from . utils import *
from bpy.types import Armature, ArmatureBones, Bone, PoseBone
from mathutils import Matrix, Vector, Euler
from mathutils.geometry import interpolate_bezier
from . import_properties import *
from . bone_shapes import *


class RigPP_OT_SplineChain(bpy.types.Operator):
    bl_idname = "rigpp.parent_to_surface_tri"
    bl_label = "Parent To Surface (triangle)"
    bl_description = "Find closes 3 vertecies on active object from selected object(s)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):

        if context.mode != "OBJECT":
            return False

        target = context.active_object
        if target is None or target.type != "MESH":
            return False

        mesh = target.data

        if len(mesh.vertices) < 3:
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

            closest3 = [0, 1, 2]
            closest3Dist = list(dist(id, location) for id in closest3)

            for i, vt in enumerate(vertices):
                if i in closest3:
                    continue

                for i, id in enumerate(closest3):
                    d = dist(id, vt.co)

                    if d<closest3Dist[i]:
                        closest3Dist[i]=d
                        closest3[i]=i
                        break
            
            for id in closest3:
                vertices[id].select=True
            
            obj.select_set(True)
            bpy.ops.object.parent_set(type='VERTEX_TRI')
            obj.select_set(False)
            
            for id in closest3:
                vertices[id].select=False
            

        for obj in toParent:
            if obj == target:
                continue
            
            obj.select_set(True)
        
        for id in orgId:
            vertices[id].select=True
        
        return {"FINISHED"}
