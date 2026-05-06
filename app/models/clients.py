from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,Integer,ForeignKey
from ..core import Base
from .abstact import BaseUserFields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Trainer,TrainerRequest,AdminRequest
    

class Client(Base,BaseUserFields):
    __tablename__ = 'users'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    age:Mapped[int] = mapped_column(Integer)
    number:Mapped[str] = mapped_column(String(40))
    
    trainer_id:Mapped[int|None] = mapped_column(ForeignKey('trainers.id'),nullable=True,default=None)
    
    trainer:Mapped["Trainer"] = relationship(back_populates='clients')
    
    client_request:Mapped[list['TrainerRequest']] = relationship(back_populates='about_client')
    to_admin_requests:Mapped[list['AdminRequest']] = relationship(back_populates= 'about_client')

    
    
