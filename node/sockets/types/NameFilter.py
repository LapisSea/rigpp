import bpy
from ....import_properties import *

def doEXAC(name,test):
    return name==test
def doEXAP(name,test):
    return test in name.split(".")
def doSTAR(name,test):
    return name.startswith(test)
def doENDW(name,test):
    return name.endswith(test)
def doCONT(name,test):
    return test in name
def doREGX(name,regex):
    import re
    return re.search(regex,name)
    
filterTypes=[
    ("EXAC","Exact","Match exactly whole name"),
    ("EXAP","Exact part","Match name if it exactly matches a part (Part is delimited by a '.')"),
    ("STAR","Starts with","Match name if it starts with"),
    ("ENDW","Ends with","Match name if it ends with"),
    ("CONT","Contains","Match name if it contrains"),
    ("REGX","Regex matches","Match name if matches regex"),
]
filters={
    "EXAC":doEXAC,
    "EXAP":doEXAP,
    "STAR":doSTAR,
    "ENDW":doENDW,
    "CONT":doCONT,
    "REGX":doREGX
}

from ...BoneNodeTree import updateTrees

class NameFilter(PropertyGroup):
    
    def filter(self,name):
        return self.value=="" or filters.get(self.type)(name,self.value)
    
    type: EnumProperty(name="type",items=filterTypes, default=filterTypes[0][0], update=updateTrees)
    value: StringProperty(name="value", update=updateTrees, options={"TEXTEDIT_UPDATE"})