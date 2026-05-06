from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,String,Text
from ..core import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Trainer,Client

class TrainerRequest(Base):
    __tablename__ = 'trainer_requests'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    
    client_id:Mapped[int] = mapped_column(ForeignKey('users.id'))
    trainer_id:Mapped[int] = mapped_column(ForeignKey('trainers.id'))
    
    status:Mapped[str] = mapped_column(String(50))
    
    about_trainer:Mapped['Trainer'] = relationship(back_populates='trainer_request')
    about_client:Mapped['Client'] = relationship(back_populates='client_request')
    
    
class AdminRequest(Base):
    __tablename__ = 'admin_request'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    description:Mapped[str] = mapped_column(Text)
    
    status:Mapped[str] = mapped_column(String(50))
    
    client_id:Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    about_client:Mapped['Client'] = relationship(back_populates='to_admin_requests')
    

    
    