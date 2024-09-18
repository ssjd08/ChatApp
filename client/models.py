class User:
    def __init__(self, username:str=None, password:str=None, email:str=None, image:str=None,
                 groups:list=None, date_joined:str=None, is_active:bool=None, is_staff:bool=None, token:str=None) -> None:
        self.token = token
        self.username = username
        self.password = password
        self.email = email
        self.image = image
        self.groups = groups
        self.date_joined = date_joined
        self.is_active = is_active
        self.is_staff = is_staff
        
    def change_info(self, username:str=None, password:str=None, email:str=None, image:str=None,
                 groups:list=None, date_joined:str=None, is_active:bool=None, is_staff:bool=None, token:str=None) -> None: 
        self.token = token
        self.username = username
        self.password = password
        self.email = email
        self.image = image
        self.groups = groups
        self.date_joined = date_joined
        self.is_active = is_active
        self.is_staff = is_staff
        
    def __str__(self):
        return f"username: {self.username}, password : {self.password}, token : {self.token}"
    
    def retrive_username(self):
        return self.username
        
class Group:
    def __init__(self, name:str, users:list, owner:User, messages:list, created_at:str, updated_at:str) -> None:
        self.name = name
        self.users = users
        self.owner = owner
        self.messages = messages
        self.created_at = created_at
        self.updated_at = updated_at
        
class Message:
    def __init__(self, content:str, author:User, group:Group, created_at:str, updated_at:str) -> None:
        self.content = content
        self.author = author
        self.group = group
        self.created_at = created_at
        self.updated_at = updated_at