from pydantic import BaseModel,Field,EmailStr,ConfigDict
from typing import Annotated,Optional
from .abstract import AbstractRegister,AbstractPatch
from .trainers import InfoAboutTrainer

class CreateUser(AbstractRegister):
    age: Annotated[int, Field(...)]
    number: Annotated[str, Field(...)]
    trainer_id: Annotated[int|None, Field(default=None)]
    
    model_config = ConfigDict(from_attributes=True)
    
class PatchClient(AbstractPatch):
    age: Annotated[Optional[int], Field(default=None,ge=18)]
    number: Annotated[str, Field(default=None)]
    
    model_config = ConfigDict(from_attributes=True) 

class InfoAboutClient(BaseModel):
    id:int
    name:Annotated[str,Field(...)]
    surname:Annotated[str,Field(...)]
    email:Annotated[EmailStr,Field(...)]
    trainer_id:Annotated[int|None, Field(default=None)]
    model_config = ConfigDict(from_attributes=True)

class LoginClient(BaseModel):
    email:Annotated[EmailStr,Field(...)]
    password:Annotated[str,Field(...)]