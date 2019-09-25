
class BoneChain:
    def __init__(self):
        self.base=[]
        self.attributes=[]
        self.controllers=[]
    
    def __str__(self):
        return "BoneChain:\n - base: "+str([b.name for b in self.base])+\
            "\n - attributes: "+str(self.attributes)