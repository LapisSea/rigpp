
import bpy
from .utils import (makeId,objModeSession,execSocket,runLater,onDepsgraph,offDepsgraph)

import os
import pickle
import json
from pathlib import Path

dataPath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_scraped")
dataPathP=Path(dataPath)


def readModuleData():
    if not os.path.exists(dataPath):
        return {}
    
    fileObject = open(dataPath,'rb')
    
    try:
        return json.load(fileObject)
    except:
        fileObject.close()
        os.remove(dataPath)
        return {}
    finally:
        fileObject.close()

def scrapeModule(name):
    return readModuleData().get(name,{"enums":[],"types":{}})

def saveModule(name, modData):
    data=readModuleData()
    data[name]=modData
    
    fileObject = open(dataPath,'wb')
    try:
        pickle.dump(data, fileObject)
    finally:
        fileObject.close()
        


editBoneAttrs=scrapeModule("editBoneAttrs")


scraped=False

def _scrape():
    
    global scraped
    if scraped:
        return
    scraped=True
    
    print("Scraping!")
    
    context=bpy.context
    
    arm=bpy.data.armatures.new("__ARM_SCRAP")
    obj=bpy.data.objects.new("__ARM_SCRAP", arm)
    context.scene.collection.objects.link(obj)
    try:
        
        def EDIT(armature):
            bone=armature.data.edit_bones.new("bone")
            
            editBoneAttrs["enums"].clear()
            editBoneAttrs["types"].clear()
            
            for k in dir(bone):
                val=getattr(bone,k)
                try:
                    setattr(bone, k,val)
                except:
                    continue
                
                typ=val.__class__.__name__
                
                
                
                editBoneAttrs["enums"].append((k," ".join([s.capitalize() for s in k.split("_")]),""))
                
                if val==None:
                    typ="NodeSocketBone"
                else:
                    if typ=="bpy_prop_array":
                        typ=val[0].__class__.__name__.capitalize()+"List"
                    else:
                        typ=typ.capitalize()
                    
                    typ="NodeSocketB"+typ
                
                editBoneAttrs["types"][k]=typ
            
            saveModule("editBoneAttrs",editBoneAttrs)
        
        
        objModeSession( obj, "EDIT", EDIT)
        
    finally:
        context.scene.collection.objects.unlink(obj)
        bpy.data.objects.remove(obj)
        bpy.data.armatures.remove(arm)


def _scrape0(scene):
    try:
        offDepsgraph(_scrape0)
    except:pass
    
    _scrape()


def causeDepsgraph():
    try:
        offDepsgraph(_scrape0)
    except:
        pass
    
    global scraped
    if scraped:
        return
    
    runLater(causeDepsgraph)
    onDepsgraph(_scrape0)
    
    # print("Causing Depsgraph")
    bpy.context.scene.gravity=bpy.context.scene.gravity
    
    return 0

runLater(causeDepsgraph)