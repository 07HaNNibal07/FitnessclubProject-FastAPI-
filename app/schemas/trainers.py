from pydantic import BaseModel,Field,EmailStr,ConfigDict
from typing import Annotated,Optional

from .abstract import AbstractRegister,AbstractPatch
 

class CreateTrainer(AbstractRegister):
    info:Annotated[str,Field(...)]
    number: Annotated[str, Field(...)]
    age: Annotated[int, Field(...)]
    
    model_config = ConfigDict(from_attributes=True)
    
class InfoAboutTrainer(BaseModel):
    id:int
    name:Annotated[str,Field(...)]
    surname:Annotated[str,Field(...)]
    info:Annotated[str,Field(...)]
    email:Annotated[EmailStr,Field(...)]
    
    model_config = ConfigDict(from_attributes=True)
   
class PatchTrainer(AbstractPatch):
    info:Annotated[Optional[int], Field(default=None)]

    model_config = ConfigDict(from_attributes=True) 