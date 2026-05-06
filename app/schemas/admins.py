from .abstract import AbstractRegister
from pydantic import BaseModel,ConfigDict,Field,EmailStr
from typing import Annotated

class CreateAdmin(AbstractRegister):
    
    model_config = ConfigDict(from_attributes=True)
    

class InfoAboutAdmin(BaseModel):
    name:Annotated[str,Field(...)]
    surname:Annotated[str,Field(...)]
    email:Annotated[EmailStr,Field(...)]
    
    model_config = ConfigDict(from_attributes=True)