from pydantic import BaseModel

class LoginInfo(BaseModel):
    email: str 
    password: str 
    nick_name: str 
    age: int