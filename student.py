'''
	Student class, extends from Person class | ctto -> Sir Dennis Durano
'''
class Student():
    def __init__(self,**args):
        self.idno = args.get('idno')
        self.lastname= args.get('lastname')
        self.firstname = args.get('firstname')
        self.midinit = args.get('midinit')
        self.course = args.get('course')
        self.level = args.get('level')
        self.username = args.get('username')
        self.password_plain = args.get('password_plain')
        self.password_hash = args.get('password_hash')
        
    def __str__(self)->dict: 
        #return f"{self.idno},{self.lastname},{self.firstname},{self.course},{self.level}"
        studenrecord = {
                'idno':self.idno,
                'lastname':self.lastname,
                'firstname':self.firstname,
                'midinit':self.midinit,
                'course':self.course,
                'level':self.level,
                'username':self.username,
                'password_plain':self.password_plain,
                'password_hash':self.password_hash
                }
        return studenrecord
        
    def __eq__(self,other)->bool: 
        if type(other) != type(self):                                       
            return False
        elif self.idno == other.idno:   
            return True
        else: 
            return False
        
    #user-defined modules
    #setters
    def setidno(self,idno:str)->None:       self.idno = idno
    def setcourse(self,course:str)->None:   self.course = course
    def setlevel(self,level:str)->None:     self.level = level
    #getters
    def getidno(self)->str:                 return self.idno
    def getlastname(self)->str:             return self.lastname
    def getfirstname(self)->str:            return self.firstname
    def getcourse(self)->str:               return self.course
    def getlevel(self)->str:                return self.level


