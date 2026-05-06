from sqlalchemy.orm import Mapped,mapped_column
from ..core import Base
from sqlalchemy import String

class BaseUserFields:
    __abstract__ = True
    
    name:Mapped[str] = mapped_column(String(40))
    surname:Mapped[str] = mapped_column(String(40))
    email:Mapped[str] = mapped_column(String(60),unique=True)
    password:Mapped[str] = mapped_column(String(250))
    is_active:Mapped[bool] = mapped_column(default=True)