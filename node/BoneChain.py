
class BoneChain:
    def __init__(self):
        self.base=[]
        self.attributes=[]
        self.controllers=[]
    
    def __str__(self):
        return "BoneChain:\n - base: "+(self.base[0][1].name+" -> "+str([b[0] for b in self.base])) if self.base else "[]"+\
            "\n - attributes: "+str(self.attributes)