from pydantic import BaseModel,Field,EmailStr,field_validator
from typing import Annotated,Optional
import re

class AbstractRegister(BaseModel):
    name:Annotated[str,Field(...)]
    surname:Annotated[str,Field(...)]
    email:Annotated[EmailStr,Field(...)]
    password:Annotated[str,Field(...,examples=['Qwerty1234'])]
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v:str):
        v = v.strip()
        pattern = r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{10,}$'
        
        if not re.match(pattern, v):
            raise ValueError(
                "Пароль должен содержать минимум 10 символов, 1 заглавную букву и 1 цифру"
            )
        return v 


class AbstractPatch(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    surname:Annotated[Optional[str],Field(default=None)]
    email:Annotated[Optional[EmailStr],Field(default=None)]
    password:Annotated[Optional[str],Field(default=None)]
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v:str):
        v = v.strip()
        pattern = r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{10,}$'
        
        if not re.match(pattern, v):
            raise ValueError(
                "Пароль должен содержать минимум 10 символов, 1 заглавную букву и 1 цифру"
            )
        return v 