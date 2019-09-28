import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)
import mathutils


ANY="NodeSocketAny"

def primitiveVal(n):
    return eval(n[1:].lower()+'("0")')

def calcMulTypes(inputs):
    
    if all(v is None for v in inputs):
        return (["BFloat","BFloat"],["BFloat"])
    
    if all(v!=None for v in inputs):
        v1=inputs[0]
        if all(v==v1 for v in inputs):
            return (inputs,[inputs[0]])
        
        if inputs[0]=="BVector":
            return (inputs,["BVector"])
        if inputs[0]=="BColor":
            return (inputs,["BColor"])
        
        try:
            if all(v.startswith("B") for v in inputs):
                mulVal=primitiveVal(inputs[0])*primitiveVal(inputs[1])
                cl="B"+mulVal.__class__.__name__.capitalize()
                
                return (inputs,[cl])
        except:
            pass
        raise Exception("not implemented: "+str(inputs))
    
    nn=next(item for item in inputs if item is not None)
    
    if all(v==None or v==nn for v in inputs):
        return ([b if b!=None else nn for b in inputs],[nn])
    
    
    raise Exception("not implemented: "+str(inputs))


from ...RGBA import RGBA

def doMul(vals,outTypes):
    outType=outTypes[0]
    l=vals[0]
    r=vals[1]
    
    
    if outType=="BColor":
        if isinstance(l,mathutils.Vector):
            return RGBA(l.x*r.r, l.y*r.g, l.z*r.b, r.a)
        if isinstance(r,mathutils.Vector):
            return RGBA(l.r*r.x, l.g*r.y, l.b*r.z, l.a)
        
        lc=isinstance(l,RGBA)
        rc=isinstance(r,RGBA)
        if lc and rc:
            return l*r
        if lc:
            return RGBA(l.r*r, l.g*r, l.b*r, l.a)
        if rc:
            return RGBA(r.r*l, r.g*l, r.b*l, r.a)
        
        raise Exception()
    
    if outType=="BVector":
        if isinstance(l,RGBA):
            return mathutils.Vector((l.r*r.x, l.g*r.y, l.b*r.z))
        if isinstance(r,RGBA):
            return mathutils.Vector((r.r*l.x, r.g*l.y, r.b*l.z))
        
        lc=isinstance(l,mathutils.Vector)
        rc=isinstance(r,mathutils.Vector)
        
        if lc and rc:
            return mathutils.Vector((l.x*r.x, l.y*r.y, l.z*r.z))
        if lc:
            return mathutils.Vector((l.x*r, l.y*r, l.z*r))
        if rc:
            return mathutils.Vector((r.x*l, r.y*l, r.z*l))
        
        raise Exception()
    
    return l*r

def safeDiv(a,b):
    if b==0:
        return math.inf
    return a/b

def doDiv(vals,outTypes):
    outType=outTypes[0]
    l=vals[0]
    r=vals[1]
    
    
    if outType=="BColor":
        if isinstance(l,mathutils.Vector):
            return RGBA(safeDiv(l.x, r.r), safeDiv(l.y, r.g), safeDiv(l.z, r.b), r.a)
        if isinstance(r,mathutils.Vector):
            return RGBA(safeDiv(l.r, r.x), safeDiv(l.g, r.y), safeDiv(l.b, r.z), l.a)
        
        lc=isinstance(l,RGBA)
        rc=isinstance(r,RGBA)
        if lc and rc:
            return l/r
        if lc:
            return RGBA(safeDiv(l.r, r), safeDiv(l.g, r), safeDiv(l.b, r), l.a)
        if rc:
            return RGBA(safeDiv(r.r, l), safeDiv(r.g, l), safeDiv(r.b, l), r.a)
        
        raise Exception()
    
    if outType=="BVector":
        if isinstance(l,RGBA):
            return mathutils.Vector((safeDiv(l.r, r.x), safeDiv(l.g, r.y), safeDiv(l.b, r.z)))
        if isinstance(r,RGBA):
            return mathutils.Vector((safeDiv(r.r, l.x), safeDiv(r.g, l.y), safeDiv(r.b, l.z)))
        
        lc=isinstance(l,mathutils.Vector)
        rc=isinstance(r,mathutils.Vector)
        
        if lc and rc:
            return mathutils.Vector((safeDiv(l.x, r.x), safeDiv(l.y, r.y), safeDiv(l.z, r.z)))
        if lc:
            return mathutils.Vector((safeDiv(l.x, r), safeDiv(l.y, r), safeDiv(l.z, r)))
        if rc:
            return mathutils.Vector((safeDiv(r.x, l), safeDiv(r.y, l), safeDiv(r.z, l)))
        
        raise Exception()
    
    return safeDiv(l,r)

def doAdd(vals,outTypes):
    
    outType=outTypes[0]
    l=vals[0]
    r=vals[1]
    
    
    if outType=="BColor":
        if isinstance(l,mathutils.Vector):
            return RGBA(l.x+r.r, l.y+r.g, l.z+r.b, r.a)
        if isinstance(r,mathutils.Vector):
            return RGBA(l.r+r.x, l.g+r.y, l.b+r.z, l.a)
        
        lc=isinstance(l,RGBA)
        rc=isinstance(r,RGBA)
        if lc and rc:
            return l+r
        if lc:
            return RGBA(l.r+r, l.g+r, l.b+r, l.a)
        if rc:
            return RGBA(r.r+l, r.g+l, r.b+l, r.a)
        
        raise Exception()
    
    if outType=="BVector":
        if isinstance(l,RGBA):
            return mathutils.Vector((l.r+r.x, l.g+r.y, l.b+r.z))
        if isinstance(r,RGBA):
            return mathutils.Vector((r.r+l.x, r.g+l.y, r.b+l.z))
        
        lc=isinstance(l,mathutils.Vector)
        rc=isinstance(r,mathutils.Vector)
        
        if lc and rc:
            return mathutils.Vector((l.x+r.x, l.y+r.y, l.z+r.z))
        if lc:
            return mathutils.Vector((l.x+r, l.y+r, l.z+r))
        if rc:
            return mathutils.Vector((r.x+l, r.y+l, r.z+l))
        
        raise Exception()
    
    return l+r

def doSub(vals,outTypes):
    outType=outTypes[0]
    l=vals[0]
    r=vals[1]
    
    
    if outType=="BColor":
        if isinstance(l,mathutils.Vector):
            return RGBA(l.x-r.r, l.y-r.g, l.z-r.b, r.a)
        if isinstance(r,mathutils.Vector):
            return RGBA(l.r-r.x, l.g-r.y, l.b-r.z, l.a)
        
        lc=isinstance(l,RGBA)
        rc=isinstance(r,RGBA)
        if lc and rc:
            return l-r
        if lc:
            return RGBA(l.r-r, l.g-r, l.b-r, l.a)
        if rc:
            return RGBA(r.r-l, r.g-l, r.b-l, r.a)
        
        raise Exception()
    
    if outType=="BVector":
        if isinstance(l,RGBA):
            return mathutils.Vector((l.r-r.x, l.g-r.y, l.b-r.z))
        if isinstance(r,RGBA):
            return mathutils.Vector((r.r-l.x, r.g-l.y, r.b-l.z))
        
        lc=isinstance(l,mathutils.Vector)
        rc=isinstance(r,mathutils.Vector)
        
        if lc and rc:
            return mathutils.Vector((l.x-r.x, l.y-r.y, l.z-r.z))
        if lc:
            return mathutils.Vector((l.x-r, l.y-r, l.z-r))
        if rc:
            return mathutils.Vector((r.x-l, r.y-l, r.z-l))
        
        raise Exception()
    
    return l-r

def calcSqrtTypes(inputs):
    val=inputs[0]
    if val==None:
        return (["Any"],["Any"])
    try:
        if val.startswith("B"):
            sVal=math.sqrt(primitiveVal(val))
            cl="B"+sVal.__class__.__name__.capitalize()
            return (inputs,[cl])
    except:
        pass
    if val=="BVector":
        return (inputs,["BVector"])
    if val=="BColor":
        return (inputs,["BColor"])
    raise Exception("not implemented: "+str(inputs))


import math
def doSqrt(vals,outTypes):
    outType=outTypes[0]
    l=vals[0]
    if outType=="BVector":
        return mathutils.Vector((math.sqrt(l.x), math.sqrt(l.y), math.sqrt(l.z)))
    if outType=="BColor":
        return RGBA(math.sqrt(l.r),math.sqrt(l.g),math.sqrt(l.b),l.a)
    return math.sqrt(l)

def doSq(vals,outTypes):
    l=vals[0]
    return doMul((l,l),outTypes)

def doPow(vals,outTypes):
    outType=outTypes[0]
    l=vals[0]
    r=vals[1]
    
    
    if outType=="BColor":
        if isinstance(l,mathutils.Vector):
            return RGBA(l.x**r.r, l.y**r.g, l.z**r.b, r.a)
        if isinstance(r,mathutils.Vector):
            return RGBA(l.r**r.x, l.g**r.y, l.b**r.z, l.a)
        
        lc=isinstance(l,RGBA)
        rc=isinstance(r,RGBA)
        if lc and rc:
            return l**r
        if lc:
            return RGBA(l.r**r, l.g**r, l.b**r, l.a)
        if rc:
            return RGBA(r.r**l, r.g**l, r.b**l, r.a)
        
        raise Exception()
    
    if outType=="BVector":
        if isinstance(l,RGBA):
            return mathutils.Vector((l.r**r.x, l.g**r.y, l.b**r.z))
        if isinstance(r,RGBA):
            return mathutils.Vector((r.r**l.x, r.g**l.y, r.b**l.z))
        
        lc=isinstance(l,mathutils.Vector)
        rc=isinstance(r,mathutils.Vector)
        
        if lc and rc:
            return mathutils.Vector((l.x**r.x, l.y**r.y, l.z**r.z))
        if lc:
            return mathutils.Vector((l.x**r, l.y**r, l.z**r))
        if rc:
            return mathutils.Vector((r.x**l, r.y**l, r.z**l))
        
        raise Exception()
    
    return l**r

def calcAddTypes(inputs):
    return calcMulTypes(inputs)

def calcAvarageTypes(inputs):
    if all(v is None for v in inputs):
        return (["BFloat","BFloat"],["BFloat"])
    
    nn=next(item for item in inputs if item is not None)
    
    return ([nn,nn],[nn])

def doAvrg(vals,outTypes):
    return doDiv((doAdd(vals,outTypes),2),outTypes)

def doAbs(vals,outTypes):
    outType=outTypes[0]
    l=vals[0]
    
    if outType=="BVector":
        return mathutils.Vector((abs(l.x), abs(l.y), abs(l.z)))
    if outType=="BColor":
        return RGBA(abs(l.r),abs(l.g),abs(l.b), l.a)
    
    return abs(vals[0])

ops=[
    ("MUL","Multiply",""),
    ("DIV","Divide",""),
    ("ADD","Add",""),
    ("SUB","Subtract",""),
    ("SQRT","Square root",""),
    ("SQ","Square",""),
    ("POW","Power",""),
    ("AVRG","Avarage",""),
    ("ABS","Absolute",""),
    # ("LOG","Logarithm",""),
    # ("MIN","Minimum",""),
    # ("MAX","Maximum",""),
    
]

opHandlers={
    "MUL": (("Multiplicand","Multiplier"),["Product"],calcMulTypes,doMul),
    "DIV": (("Numerator","Denominator"),["Fraction"],calcMulTypes,doDiv),
    "ADD": (("Addend","Addend"),["Sum"],calcAddTypes,doAdd),
    "SUB": (("Minuend","Subtrahend"),["Difference"],calcAddTypes,doSub),
    "SQRT":(["Radicand"],["Root"],calcSqrtTypes, doSqrt),
    "SQ":(["Base"],["Square"],lambda vals:calcMulTypes([vals[0], vals[0]]), doSq),
    "POW":(("Base","Exponent"),["Power"],lambda vals:calcMulTypes([vals[0], vals[1]]), doPow),
    "AVRG":(["Value 1","Value 2"],["Avarage"],calcAvarageTypes, doAvrg),
    "ABS": (["Value"],["Absolute"],lambda vals:calcMulTypes([vals[0], "BInt"]),doAbs),
}

class Math(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Math'
    bl_icon = 'PLUS'
    
    op:EnumProperty(items=ops,name="Operation",default="MUL", update=valChange)
    
    def getHandler(self):
        return opHandlers[self.op]
    
    def doIO(self):
        
        def sync(names,types,sockets):
            inpC=len(names)
            
            for i in range(inpC):
                name=names[i]
                typ=types[i]
                
                if len(sockets)<=i:
                    sockets.new(ANY,name)
                    continue
                
                sock=sockets[i]
                
                if sock.name!=name:
                    sock.name=name
                
                self.setType(sockets,i,typ)
            
            while len(sockets)>inpC:
                inp=sockets[len(sockets)-1]
                tree=self.getTree()
                
                if not sockets[inpC-1].links:
                    for link in inp.links:
                        tree.links.new(link.from_socket, sockets[inpC-1])
                
                sockets.remove(inp)
        
        handler=self.getHandler()
        
        inputs=[]
        
        for i in range(len(handler[0])):
            if len(self.inputs)<=i:
                inputs.append(None)
                continue
            
            links=self.inputs[i].links
            if not links:
                inputs.append(None)
                continue
            
            nam=links[0].from_socket.bl_idname
            
            if nam==ANY:
                inputs.append(None)
                continue
            
            inputs.append(nam.replace("NodeSocket",""))
        
        types=handler[2](inputs)
        
        def fixName(arr):
            for i in range(len(arr)):
                arr[i]="NodeSocket"+arr[i]
            return arr
        
        sync(handler[0],fixName(types[0]),self.inputs )
        sync(handler[1],fixName(types[1]),self.outputs)
    
    def update(self):
        self.doIO()
    
    def init(self, context):
        self.doIO()
    
    def setType(self,sockets,pos,typ):
        
        inp=sockets[pos]
        
        if inp.bl_idname==typ:
            return
        
        name=inp.name
        socks=[e.to_socket if inp.is_output else e.from_socket for e in inp.links]
        
        sockets.remove(inp)
        
        new=sockets.new(typ,name)
        
        tree=self.getTree()
        
        for socket in socks:
            if new.is_output:
                tree.links.new(new, socket)
            else:
                tree.links.new(socket,new)
        
        p1=len(sockets)-1
        if p1!=pos:
            sockets.move(p1,pos)
        
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"op",text="")
        
    def execute(self,context, socket, data):
        return self.getHandler()[3]([execSocket(inp, context, data) for inp in self.inputs], [o.bl_idname.replace("NodeSocket","") for o in self.outputs])