from sqlalchemy.orm import Mapped,mapped_column,relationship
from ..core import Base
from sqlalchemy import String,Text,Integer
from .abstact import BaseUserFields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Client,TrainerRequest

class Trainer(Base,BaseUserFields):
    __tablename__ = 'trainers'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    
    age:Mapped[int] = mapped_column(Integer)
    info:Mapped[str] = mapped_column(Text)
    
    number:Mapped[str] = mapped_column(String(40))

    clients:Mapped[list['Client']] = relationship(back_populates='trainer')
    
    trainer_request:Mapped[list['TrainerRequest']] = relationship(back_populates='about_trainer')