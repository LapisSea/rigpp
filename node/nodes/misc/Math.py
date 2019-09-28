import bpy
import os

from ... import BoneNode
from ....utils import (makeId,execSocket)
from ....import_properties import *

from ...sockets.types.NameFilter import NameFilter
from ...BoneNodeTree import (updateTrees,valChange)
import mathutils

from ...RGBA import RGBA


ANY="NodeSocketAny"

def primitiveVal(n):
    return eval(n[1:].lower()+'("0")')

def doSingleMathOp(l,outTypes,op):
    outType=outTypes[0]
    if outType=="BVector":
        return mathutils.Vector((op(l.x), op(l.y), op(l.z)))
    if outType=="BColor":
        return RGBA(op(l.r),op(l.g),op(l.b),l.a)
    return op(l)

def doLRMathOp(l,r,outType,op):
    
    if outType=="BColor":
        if isinstance(l,mathutils.Vector):return RGBA(op(l.x, r.r), op(l.y, r.g), op(l.z, r.b), r.a)
        if isinstance(r,mathutils.Vector):return RGBA(op(l.r, r.x), op(l.g, r.y), op(l.b, r.z), l.a)
        
        lc=isinstance(l,RGBA)
        rc=isinstance(r,RGBA)
        if lc and rc:return l/r
        if lc:return RGBA(op(l.r, r), op(l.g, r), op(l.b, r), l.a)
        if rc:return RGBA(op(r.r, l), op(r.g, l), op(r.b, l), r.a)
        
        raise Exception()
    
    if outType=="BVector":
        if isinstance(l,RGBA):return mathutils.Vector((op(l.r, r.x), op(l.g, r.y), op(l.b, r.z)))
        if isinstance(r,RGBA):return mathutils.Vector((op(r.r, l.x), op(r.g, l.y), op(r.b, l.z)))
        
        lc=isinstance(l,mathutils.Vector)
        rc=isinstance(r,mathutils.Vector)
        
        if lc and rc:return mathutils.Vector((op(l.x, r.x), op(l.y, r.y), op(l.z, r.z)))
        if lc:return mathutils.Vector((op(l.x, r), op(l.y, r), op(l.z, r)))
        if rc:return mathutils.Vector((op(r.x, l), op(r.y, l), op(r.z, l)))
        
        raise Exception()
    
    return op(l,r)


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
        
        if inputs[1]=="BVector":
            return (inputs,["BVector"])
        if inputs[1]=="BColor":
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


def doMul(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],lambda l,r:l*r)

def safeDiv(a,b):
    if b==0:
        return math.inf
    return a/b

def doDiv(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],safeDiv)

def doAdd(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],lambda l,r:l+r)

def doSub(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],lambda l,r:l-r)

def calcSqrtTypes(inputs):
    val=inputs[0]
    if val==None:
        return (["BFloat"],["BFloat"])
    
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
    return doSingleMathOp(vals[0],outTypes,math.sqrt)

def doSq(vals,outTypes):
    l=vals[0]
    return doMul((l,l),outTypes)

def doPow(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],lambda l,r:l**r)

def calcAddTypes(inputs):
    return calcMulTypes(inputs)

def calcAvarageTypes(inputs):
    if all(v is None for v in inputs):
        return (["BFloat","BFloat"],["BFloat"])
    
    nn=next(item for item in inputs if item is not None)
    
    return ([nn if i==None else i for i in inputs],[nn])

def doAvrg(vals,outTypes):
    return doDiv((doAdd(vals,outTypes),2),outTypes)

def doAbs(vals,outTypes):
    return doSingleMathOp(vals[0],outTypes,abs)

def doLog(vals,outTypes):
    return doSingleMathOp(vals[0],outTypes,math.log)

def doMin(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],min)
    
def doMax(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],max)

def calcLessTypes(inputs):
    if all(v is None for v in inputs):
        return (["BFloat","BFloat"],["BBool"])
    
    for i in range(len(inputs)):
        v=inputs[i]
        inputs[i]="BFloat" if v in ("BColor","BVector") else v
    
    nn=next(item for item in inputs if item is not None)
    
    return ([nn if i==None else i for i in inputs],["BBool"])

def doLess(vals,outTypes):
    return doLRMathOp(vals[0],vals[1],outTypes[0],lambda l,r:l<r)

def doGret(vals,outTypes):
    print()
    return doLRMathOp(vals[0],vals[1],outTypes[0],lambda l,r:l>r)

def calcSinTypes(inputs):
    try:
        float(primitiveVal(inputs[0]))
        return (inputs,["BFloat"])
    except:
        return (["BFloat"],["BFloat"])

def doSin(vals,outTypes):
    return math.sin(vals[0])

def doCos(vals,outTypes):
    return math.cos(vals[0])

def doTan(vals,outTypes):
    return math.tan(vals[0])

def calcAtan2Types(inputs):
    if (inputs[1]==None and inputs[0]=="BVector") or (inputs[0]==None and inputs[1]=="BVector"):
        return (["BVector"],["BFloat"])
        
    try:
        float(primitiveVal(inputs[0]))
    except:
        inputs[0]="BFloat"
    try:
        float(primitiveVal(inputs[1]))
    except:
        inputs[1]="BFloat"
    
    return (inputs,["BFloat"])

def doAtan2(vals,outTypes):
    try:
        v=vals[0]
        return math.atan2(v[0],v[1])
    except:
        pass
    return math.atan2(vals[0],vals[1])


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
    ("LOG","Logarithm",""),
    ("MIN","Minimum",""),
    ("MAX","Maximum",""),
    ("LESS","Less than",""),
    ("GRET","Greater than",""),
    ("SIN","Sine",""),
    ("COS","Cosine",""),
    ("TAN","Tangent",""),
    ("ATAN2","Arctan2",""),
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
    "LOG": (["Antilogarithm"],["Logarithm"],lambda vals:calcMulTypes([vals[0], "BFloat"]),doLog),
    "MIN":(["Value 1","Value 2"],["Minimum"],calcAvarageTypes, doMin),
    "MAX":(["Value 1","Value 2"],["Maximum"],calcAvarageTypes, doMax),
    "LESS":(["Value","Limit"],["Is less"],calcLessTypes, doLess),
    "GRET":(["Value","Limit"],["Is greater"],calcLessTypes, doGret),
    "SIN":(["Angle"],["Value"],calcSinTypes, doSin),
    "COS":(["Angle"],["Value"],calcSinTypes, doCos),
    "TAN":(["Angle"],["Value"],calcSinTypes, doTan),
    "ATAN2":(["Value","Value"],["Angle"],calcAtan2Types, doAtan2),
}

class Math(BoneNode):
    bl_idname = makeId(os.path.basename(__file__)[:-3])
    bl_label = 'Math'
    bl_icon = 'PLUS'
    
    def opChange(self,ctx):
        self.doIO()
        valChange(self,ctx)
    
    op:EnumProperty(items=ops,name="Operation",default="MUL", update=opChange)
    
    def getHandler(self):
        return opHandlers[self.op]
    
    def doIO(self):
        
        def sync(names,types,sockets):
            
            
            inpC=len(names)
            typLen=len(types)
            
            
            if inpC>typLen:
                names=names[0:typLen]
                inpC=len(names)
            
            
            for i in range(inpC):
                name=names[i]
                typ=types[i]
                
                if len(sockets)<=i:
                    sockets.new(typ,name)
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
        isOut=inp.is_output
        socks=[e.to_socket if isOut else e.from_socket for e in inp.links]
        
        sockets.remove(inp)
        new=sockets.new(typ,name)
        
        p1=len(sockets)-1
        if p1!=pos:
            sockets.move(p1,pos)
        
        tree=self.getTree()
        
        for socket in socks:
            if isOut:
                print(tree.links.new(new, socket))
            else:
                tree.links.new(socket,new)
        
    
    def draw_buttons(self, context, layout):
        layout.prop(self,"op",text="")
        
    def execute(self,context, socket, data):
        return self.getHandler()[3]([execSocket(inp, context, data) for inp in self.inputs], [o.bl_idname.replace("NodeSocket","") for o in self.outputs])