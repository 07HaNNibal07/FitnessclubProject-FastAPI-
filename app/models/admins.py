from sqlalchemy.orm import Mapped,mapped_column
from ..core import Base
from sqlalchemy import String
from .abstact import BaseUserFields

class Admin(Base,BaseUserFields):
    __tablename__ = 'admins'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    