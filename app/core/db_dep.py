from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine,AsyncSession
from .config import settings 
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData



class Base(DeclarativeBase):
    pass

class DB_Dependency:
    def __init__(self,url:str,echo:bool):
        self.engine = create_async_engine(url=url,echo=echo)  
        self.session_factory = async_sessionmaker(bind = self.engine,expire_on_commit=False,class_=AsyncSession)
    
    async def current_session(self):
        async with self.session_factory() as session:
            yield session

db_helper = DB_Dependency(settings.db_settings.db_url,settings.db_settings.db_echo)