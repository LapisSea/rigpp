from .BoneNodeTree import TREE_ID
from bpy.types import Node,NodeSocket
import nodeitems_utils
from ..utils import (makeId,execNode,execSocket)
import bpy
from ..import_properties import *

import sys
sys.path.insert(0, '..')


class BoneNodeSocket(NodeSocket):
    bl_label = 'Bone Node Socket'
    display_shape="DIAMOND"
    
    
    def draw(self, context, layout, node, text):
        
        def doText():
            
            tree=context.space_data.edit_tree
            
            if hasattr(tree,"run_cache"):
                run_cache=tree.run_cache
                
                def fetch(data):
                    try:
                        return data[node.name][self.identifier]
                    except:
                        return None
                
                data=fetch(run_cache["outputs"])
                if data==None:
                    try:
                        for group in run_cache["group_outputs"].values():
                            data=fetch(group)
                            if data!=None:
                                break
                    except:
                        pass
                
                if data!=None:
                    return text + getattr(self, "customText", str)(data)
            
            return text
        
        def drawPropDefault(lay, tex):
            if "value" in self:
                lay.prop(self, "value", text=tex)
            else:
                lay.label(text=tex)
        
        if hasattr(self,"selfTerminator") and self.selfTerminator:
            # print(self.selfTerminator)
            getattr(self,"drawProp",drawPropDefault)(layout, doText())
        elif self.is_output:
            layout.label(text=doText())
        elif self.is_linked:
            layout.label(text=text)
        else:
            getattr(self,"drawProp",drawPropDefault)(layout, doText())
    
    def execute(self,context, data):
        
        getV=None
        if hasattr(self,"getValue"):
            getV=self.getValue
        elif hasattr(self,"value"):
            getV=lambda:self.value
        else:
            getV=lambda: None
        
        
        if not self.is_linked:
            if self.is_output:
                if self.selfTerminator:
                    return getV()
                return None
            else:
                return getV()
        
        if self.is_output:
            return execNode(self.node,self,context,data)
        
        links=self.links
        if not links:
            return getattr(self,"value",None)
        
        return execSocket(links[0].from_socket, context,data)

class BoneNodeSocketList(NodeSocket):
    bl_label = 'Bone Node Socket'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        listShape="DIAMOND"
        if self.display_shape!=listShape:
            self.display_shape=listShape
    
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
        changed=[False]
        if hasattr(self,"rules"):
            
            def ADDAPTIVE_SOCKET(data):
                target=data["target"]
                listAgnostic=data.get("list_agnostic",False)
                acceptedTypes=data["accepted_types"] if "accepted_types" in data else None
                default=data.get("default",None)
                autoRename=data.get("auto_rename",True)
                
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
                    
                    c=self.setIOType(sockets, index, socketType)
                    if c:
                        if autoRename:
                            n=sockets[index].name
                            
                            hasS=n.endswith("s")
                            
                            if socketType.endswith("List"):
                                if not hasS:
                                    n+="s"
                            else:
                                if hasS:
                                    n=n[:-1]
                            
                            sockets[index].name=n
                        
                        changed[0]=True
            
            
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
                    
                    c=self.setIOType(toSocks,index, fromSock.bl_idname)
                    if c:
                        changed[0]=True
                
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
                        
                        c=self.setIOType(toSocks,index, typ)
                        if c:
                            changed[0]=True
                
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
                
                try:
                    loc[key](rule[1])
                # except IndexError as e:
                #     import traceback
                #     traceback.print_exc()
                except:
                    import traceback
                    traceback.print_exc()
            
        
        return changed[0]
    
    def getTree(self, context=None):
        if context==None:
            context=bpy.context
        return context.space_data.edit_tree
    
    def setIOType(self,sockets,pos,typ):
        
        inp=sockets[pos]
        
        if inp.bl_idname==typ:
            return False
        
        if not isinstance(typ,str):
            raise Exception("typ arg not string")
        
        name=inp.name
        isOut=inp.is_output
        socks=[e.to_socket if isOut else e.from_socket for e in inp.links]
        
        tree=self.getTree()
        alreadyStarted=tree.blockUpdates
        
        if not alreadyStarted: tree.startMultiChange()
        
        
        sockets.remove(inp)
        new=sockets.new(typ,name)
        
        
        p1=len(sockets)-1
        if p1!=pos:
            sockets.move(p1,pos)
        
        
        for socket in socks:
            if isOut:
                tree.links.new(new, socket)
            else:
                tree.links.new(socket,new)
        
        if not alreadyStarted: tree.endMultiChange()
        
        return True

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

from .socket_generator import generated_classes
classes+=generated_classes

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
