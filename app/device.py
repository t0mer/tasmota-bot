class Device:
    user: str
    password: str
    ip: str
    name: str
    status:str
    
    def __init__(self,name: str, user:str,password:str,ip:str,status:str = "off"):
        self.name = name
        self.user = user
        self.password = password
        self.ip = ip
        self.status = status