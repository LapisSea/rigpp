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
    
    def draw(self, context, layout, node, text):
        def doText():
            tree=context.space_data.edit_tree
            
            if hasattr(tree,"run_cache"):
                run_cache=tree.run_cache
                try:
                    data=run_cache["outputs"][node.name][self.identifier]
                    if data:
                        return text + " ("+str(len(data)) + ")"
                except:
                    pass
            
            return text
            
        layout.label(text=doText())
    
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
    
    def updateRules(self):
        if hasattr(self,"rules"):
            
            def ADDAPTIVE_SOCKET(data):
                target=data["target"]
                listAgnostic=data.get("list_agnostic",False)
                acceptedTypes=data["accepted_types"] if "accepted_types" in data else None
                default=data.get("default",None)
                
                if callable(target):
                    target=target(self)
                if callable(listAgnostic):
                    listAgnostic=listAgnostic(self)
                if callable(acceptedTypes):
                    acceptedTypes=acceptedTypes(self)
                if callable(default):
                    default=default(self)
                
                def getSocks(typ):
                    if typ=="input":return self.inputs
                    elif typ=="output":return self.outputs
                    else:raise Exception("ADDAPTIVE_SOCKET target needs to be input or output")
                    
                sockets=getSocks(target[0])
                
                
                
                index=target[1]
                
                socket=sockets[index]
                links=socket.links
                
                if not isinstance(index,int):
                    for i, sock in enumerate(sockets):
                        if sock==socket:
                            index=i
                
                socketType=default
                
                if links:
                    link=links[0]
                    
                    connected=link.to_socket if socket.is_output else link.from_socket
                    typ=connected.bl_idname
                    
                    if acceptedTypes==None:
                        socketType=typ
                    else:
                        testType=typ[:-4] if listAgnostic and typ.endswith("List") else typ
                        if testType in acceptedTypes:
                            socketType=typ
                
                
                if socketType!=None:
                    self.setIOType(sockets,index, socketType)
            
            
            def MIRROR_TYPE(data):
                fr=data["from"]
                toL=data["to"]
                
                if callable(fr):
                    fr=fr(self)
                if callable(toL):
                    toL=toL(self)
                
                def getSocks(typ):
                    if typ=="input":return self.inputs
                    elif typ=="output":return self.outputs
                    else: raise Exception("MIRROR_TYPE target needs to be input or output")
                
                
                fromSock=getSocks(fr[0])[fr[1]]
                
                def do(to):
                    toSocks=getSocks(to[0])
                    index=to[1]
                    target=toSocks[index]
                    
                    if not isinstance(index,int):
                        for i, sock in enumerate(toSocks):
                            if sock==target:
                                index=i
                    
                    self.setIOType(toSocks,index, fromSock.bl_idname)
                
                if isinstance(toL,list):
                    for to in toL:
                        do(to)
                else:
                    do(toL)
            
            def MIRROR_IS_LIST(data):
                fr=data["from"]
                toL=data["to"]
                
                if callable(fr):
                    fr=fr(self)
                if callable(toL):
                    toL=toL(self)
                
                def getSocks(typ):
                    if typ=="input":return self.inputs
                    elif typ=="output":return self.outputs
                    else:raise Exception("MIRROR_IS_LIST target needs to be input or output")
                
                
                fromSock=getSocks(fr[0])[fr[1]]
                fromSockIsList=fromSock.bl_idname.endswith("List")
                
                def do(to):
                    toSocks=getSocks(to[0])
                    index=to[1]
                    target=toSocks[index]
                    
                    typ=target.bl_idname
                    
                    typIsList=typ.endswith("List")
                    
                    if typIsList!=fromSockIsList:
                        if typIsList:
                            typ=typ[:-4]
                        if fromSockIsList:
                            typ=typ+"List"
                        
                        if not isinstance(index,int):
                            for i, sock in enumerate(toSocks):
                                if sock==target:
                                    index=i
                        
                        self.setIOType(toSocks,index, typ)
                
                if isinstance(toL,list):
                    for to in toL:
                        do(to)
                else:
                    do(toL)
            
            loc=locals()
            for rule in self.rules:
                key=rule[0]
                if key == "self":
                    raise Exception()
                loc[key](rule[1])
                
    
    def getTree(self, context=None):
        if context==None:
            context=bpy.context
        return context.space_data.edit_tree
    
    def setIOType(self,sockets,pos,typ):
        
        inp=sockets[pos]
        
        if inp.bl_idname==typ:
            return
        
        if not isinstance(typ,str):
            raise Exception("typ arg not string")
        
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
