
def ANUM(name,value):
    segments=name.split(".")
    if len(segments)==1:
        segments.append("000")
    
    if len(segments)>1:
        try:
            num=int(segments[-1])
            segments[-1]=str(num+1).zfill(3)
        except:
            segments.append("001")
            pass
    
    return ".".join(segments)

def ADDP(name,value):
    from .utils import makeName
    
    return makeName(name, value)

def REMP(name,value):
    segments=name.split(".")
    try:
        segments.remove(value)
    except:
        pass
    return ".".join(segments)

def NEWN(name,value):
    return value

class __name_deriver(object):
    
    def __init__(self):
        self.types=[
            ("ANUM","Append number", "The blender default way"),
            ("ADDP","Add name part", "Adds name part to the end of the name (other_thing + Thing.subthing.001 = Thing.subthing.other_thing.001"),
            ("REMP","Remove name part", "Removes name part at the end of the name (Thing.subthing.other_thing.001 - other_thing = Thing.subthing.001)"),
            ("NEWN", "New name", "Use a new unrelated name")
        ]
    
    def derive(self, type, name, value):
        return {
            "ANUM": ANUM,
            "ADDP": ADDP,
            "REMP": REMP,
            "NEWN": NEWN,
        }[type](name,value)

name_deriver=__name_deriver()
