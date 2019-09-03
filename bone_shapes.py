import bpy
import math
from . utils import *


def __box(w, h, thicc):
    return [[-w, 0, thicc], [-w, h, thicc], [w, h, thicc], [w, 0, thicc], [-w, 0, -thicc], [-w, h, -thicc], [w, h, -thicc], [w, 0, -thicc]], [], [[0, 1, 2, 3], [7, 6, 5, 4]]

def __circle(rad1,rad2, res, offset=0, cords="XZ"):
    verts = []
    edges = []
    c1="XYZ".index(cords[0].upper())
    c2="XYZ".index(cords[1].upper())
    c3=0
    
    if c1==c3 or c2==c3:
        c3=1
    if c1==c3 or c2==c3:
        c3=2
    
    for i in range(res):
        f = i/res*math.pi*2
        arr=[0,0,0]
        
        arr[c1]=math.sin(f)*rad1
        arr[c2]=math.cos(f)*rad2
        arr[c3]=offset
        
        verts.append(arr)
        
        edges.append([i, (i+1) % res])
    
    return verts, edges, []
    
def makeArmatureShape(name, gen):
    name = "ArmatureShape."+name

    col, new = makeOrGetCollection("_ArmatureShapes")
    if new:
        col.hide_render = True
        col.hide_viewport = True

    if name in col.objects:
        return col.objects[name]

    v, e, f = gen()
    obj = newMeshObject(name, col, v, e, f)

    return obj



def getIKShape():
    return makeArmatureShape("IK", lambda: __circle(0.3,0.3,30))


def getFKShape():

    def make():
        res = 30
        verts, edges, faces=__circle(0.3,0.3,res,0.5)

        verts.append([0, 0, 0])
        verts.append([0, 1, 0])
        edges.append([res, res+1])
        
        return verts, edges, faces

    return makeArmatureShape("FK", make)


def getCtrlPShape():
    return makeArmatureShape("IK<->FK Ctrl", lambda: __box(0.02, 1.08, 0.0001))


def getCtrlShape():
    return makeArmatureShape("IK<->FK Ctrl.Parent", lambda: __box(0.15, 0.08, 0.002))


def getSplineCtrlShape():

    def make():
        res = 30
        verts, edges, faces=__circle(0.3,0.3,30, 0, "XY")

        verts.append([0, 0, -0.2])
        verts.append([0, 0, 0.2])
        edges.append([res, res+1])
        
        return verts, edges, faces
        
    return makeArmatureShape("Spline Ctrl", make)



def getTweakShape():

    def make():
        res = 30
        verts, edges, faces=__circle(0.3,0.3,30, 0, "XY")

        verts.append([0, 0, -0.2])
        verts.append([0, 0, 0.2])
        edges.append([res, res+1])
        
        return verts, edges, faces
        
    return makeArmatureShape("Spline Ctrl", make)

