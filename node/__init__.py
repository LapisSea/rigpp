from .BoneNodeTree import TREE_ID
from bpy.types import Node,NodeSocket
import nodeitems_utils
from ..utils import (makeId,execNode,execSocket)
import bpy

import sys
sys.path.insert(0, '..')


class BoneNodeSocket(NodeSocket):
    bl_label = 'Bone Node Socket'
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return getattr(self,"value",None)
        
        return execSocket(links[0].from_socket, context,data)

class BoneNodeSocketList(NodeSocket):
    bl_label = 'Bone Node Socket'
    
    def execute(self,context, data):
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return []
        
        return execSocket(links[0].from_socket, context,data)

class BoneNode(Node):
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == TREE_ID
    
    def getTree(self, context=None):
        if context==None:
            context=bpy.context
        return context.space_data.edit_tree
    
    def setIOType(self,sockets,pos,typ):
        
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
                tree.links.new(new, socket)
            else:
                tree.links.new(socket,new)
        

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
        
        try:
            bpy.utils.unregister_class(cl)
            bpy.utils.register_class(cl)
            print("Already registered:", cl)
            continue
        except:
            ...
        
        bpy.utils.register_class(cl)
        

    nodeitems_utils.register_node_categories("RIGPP_NODES", node_categories)


def dereg():
    nodeitems_utils.unregister_node_categories("RIGPP_NODES")

    for cl in classes:
        try:
            bpy.utils.unregister_class(cl)
        except:
            print("Failed to unregister", cl)
