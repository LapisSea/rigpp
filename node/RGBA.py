
class RGBA():
    
    def __init__(self, r=1,g=1,b=1,a=1):
        try:
            self.r=r[0]
            self.g=r[1]
            self.b=r[2]
            self.a=r[3]
        except:
            self.r=r
            self.g=g
            self.b=b
            self.a=a
    
    def __getitem__(self, name):
        if name==0:
            return self.r
        if name==1:
            return self.g
        if name==2:
            return self.b
        if name==3:
            return self.a
        
        raise KeyError(name)
    
    def __mul__(self, n):
        return RGBA(self.r*n.r, self.g*n.g, self.b*n.b, self.a*n.a)
    def __div__(self, n):
        return RGBA(self.r/n.r, self.g/n.g, self.b/n.b, self.a/n.a)
    
    def __str__(self):
        return "Col({0:.3f}, {1:.3f}, {2:.3f}, {3:.3f})".format(self.r,self.g,self.b,self.a)