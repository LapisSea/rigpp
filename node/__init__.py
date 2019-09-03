from .BoneNodeTree import TREE_ID
from bpy.types import Node
import nodeitems_utils
from ..utils import makeId
import bpy

import sys
sys.path.insert(0, '..')


class BoneNode(Node):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == TREE_ID

class BoneNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == TREE_ID

import os
from os import listdir
from os.path import isfile, join

def addAllFrom(path, classes):
    import sys
    import importlib
    
    mypath = os.path.dirname(os.path.realpath(__file__))+"/"+path.replace(".", "/")+"/"
    names = [f[:-3] for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith(".py")]
    
    for n in names:
        exec("from ."+path+" import "+n)
        inp = locals()[n]
        clas = getattr(inp, n)
        if clas not in classes:
            classes.append(clas)

from .nodes.armature.DuplicateArmature import DuplicateArmature

classes = []
addAllFrom("sockets.types", classes)
addAllFrom("sockets", classes)
addAllFrom("nodes", classes)

mypath = join(os.path.dirname(os.path.realpath(__file__)),"nodes")

node_categories=[]

for category in listdir(mypath):
    if category.startswith("__") or isfile(join(mypath, category)):
        continue
    
    addAllFrom("nodes."+category, classes)
    
    p=join(mypath,category)
    
    node_categories.append(BoneNodeCategory(
        makeId(category).replace(".","_"),
        category.capitalize(),
        items=[nodeitems_utils.NodeItem(makeId(f[0:-3])) for f in listdir(p) if isfile(join(p, f))]
    ))


def reg():
    for cl in classes:
        bpy.utils.register_class(cl)

    nodeitems_utils.register_node_categories("RIGPP_NODES", node_categories)


def dereg():
    nodeitems_utils.unregister_node_categories("RIGPP_NODES")

    for cl in classes:
        bpy.utils.unregister_class(cl)
