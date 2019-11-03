import bpy
from ....import_properties import *

from ...BoneNodeTree import updateTrees

types=[]

def addType(name):
    nam=""
    for c in name[10:]:
        if nam!="" and c.isupper():
            nam+=" "
        nam+=c
    
    if nam.startswith("B "):
        nam=nam[2:]
    
    types.append((name,nam,""))

import os
from os import listdir
from os.path import isfile, join
import sys
import importlib

mypath = os.path.dirname(os.path.realpath(__file__))+"/../"
for f in listdir(mypath):
    if f.endswith(".py") and isfile(join(mypath, f)):
        addType(f[:-3])

class SocketReference(PropertyGroup):
    sockType: EnumProperty(name="Type", items=types,update=updateTrees)
    name: StringProperty(name="value", update=updateTrees)
    
    def __str__(self):
        return "SocketReference(sockType={0:s}, name={1:s})".format(self.sockType,self.name)
