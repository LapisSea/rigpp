

class BoneRef():
    
    @classmethod
    def fromBone(cls,armature, bone):
        return BoneRef(armature, bone.name)
    
    def __init__(self, armature, name):
        self.armature=armature
        self.name=name
    
    def __str__(self):
        return "{0:s} → {1:s}".format(self.armature.name, self.name)
    
    def getBone(self):
        try:
            return self.armature.data.bones[self.name]
        except KeyError as e:
            return None
    
    def getEditBone(self):
        try:
            return self.armature.data.edit_bones[self.name]
        except KeyError as e:
            return None
    
    def getPoseBone(self):
        try:
            return self.armature.pose.bones[self.name]
        except KeyError as e:
            return None
    
    def __getitem__(self, i):
        if i!=0:
            raise Exception()
        
        return self
    
    def __len__(self):
        return 1

class BoneRefList():
    
    @classmethod
    def fromBones(cls,armature, bones):
        return BoneRefList([BoneRef.fromBone(armature,b) for b in bones])
    
    def __init__(self, refs):
        arm=None
        for r in refs:
            if not r:
                continue
            a=r.armature
            
            if arm==None:
                arm=a
            elif arm!=a:
                raise Exception(arm.name+" / "+a.name)
        
        self.refs=refs
        self.armature=arm
        
    def getBones(self):
        return [b.getBone() for b in self.refs]
        
    def getEditBones(self):
        return [b.getEditBone() for b in self.refs]
        
    def getPoseBones(self):
        return [b.getPoseBone() for b in self.refs]
    
    def __str__(self):
        if not self.armature:
            return "[x] → []"
        
        return "{0:s} → {1:s}".format(self.armature.name, ", ".join(r.name if r!=None else "[X]" for r in self.refs))
    
    def __getitem__(self, i):
        return self.refs[i]
    
    def __len__(self):
        return len(self.refs)