
import bpy
from .utils import (makeId,objModeSession,execSocket,runLater,onDepsgraph,offDepsgraph)

import os
import pickle
import json
from pathlib import Path

dataPath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_scraped")
dataPathP=Path(dataPath)

# ioImpl=json
# rwAddon=""
ioImpl=pickle
rwAddon="b"

def readModuleData():
    if not os.path.exists(dataPath):
        return {}
    
    fileObject = open(dataPath,'r'+rwAddon)
    
    try:
        obj=ioImpl.load(fileObject)
        
        try:
            for block in obj.values():
                if "enums" not in block:
                    continue
                
                enums=block["enums"]
                for i in range(len(enums)):
                    enums[i]=(*(enums[i]),)
        except:
            # import traceback
            # traceback.print_exc()
            pass
        
        return obj
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
    
    fileObject = open(dataPath,'w'+rwAddon)
    try:
        ioImpl.dump(data, fileObject)
    finally:
        fileObject.close()
        


editBoneAttrs=scrapeModule("editBoneAttrs")
boneConstraints=scrapeModule("boneConstraints")


scraped=False

def discoverType(obj, k):
    def dummy():pass
    
    try:
        setattr(obj, k, dummy)
    except Exception as e:
        msg=str(e)
        
        start="expected a "
        expected=msg[msg.index(start)+len(start):msg.index(", not")]
        
        typeMark=" type"
        if expected.endswith(typeMark):
            expected=expected[0:-len(typeMark)]
        
        if expected.endswith("Bone"):
            expected="Bone"
        
        return expected
    
    raise Exception("This should never happen "+str(obj)+" "+str(k))

def scanWritableAttributes(obj):
    
    enums=[]
    types={}
    
    for k in dir(obj):
        if k.startswith("__"):
            continue
        
        val=getattr(obj,k)
        try:
            setattr(obj, k,val)
        except:
            continue
        
        typ=val.__class__.__name__
        
        if val==None or val=="str":
            typ=discoverType(obj,k)
        
        if typ=="bpy_prop_array":
            if len(val)==0:
                print("Ignored",val)
                continue
            
            typ=val[0].__class__.__name__.capitalize()+"List"
        else:
            typ=typ.capitalize()
        
        typ="NodeSocketB"+typ
        
        enums.append((k," ".join([s.capitalize() for s in k.split("_")]),""))
        types[k]=typ
    
    return (enums, types)

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
            
            bone.tail=(0,0,0)
            bone.head=(0,1,0)
            
            en,ty = scanWritableAttributes(bone)
            
            editBoneAttrs["enums"].clear()
            editBoneAttrs["enums"].extend(en)
            
            editBoneAttrs["types"].clear()
            editBoneAttrs["types"].update(ty)
            
            saveModule("editBoneAttrs",editBoneAttrs)
        
        def POSE(armature):
            bone=armature.pose.bones["bone"]
            
            constraints=None
            try:
                bone.constraints.new("bad name")
            except Exception as e:
                types=str(e)
                types=types[types.index("not found in"):]
                types=types[types.index("("):]
                types=types.replace("(, ", "(")
                constraints=eval(types)
            
            boneConstraints["enums"].clear()
            
            for constraint in constraints:
                c=bone.constraints.new(constraint)
                
                en,keys = scanWritableAttributes(c)
                
                k=constraint
                boneConstraints["enums"].append((k," ".join([s.capitalize() for s in k.split("_")]),""))
                boneConstraints["types"][k]=keys
            
            saveModule("boneConstraints",boneConstraints)
        
        objModeSession( obj, "EDIT", EDIT, "POSE", POSE)
        
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