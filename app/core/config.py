from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import BaseModel,Field

BASE_DIR = Path(__file__).parent.parent


class DBSettings(BaseModel):
    db_url: str 
    db_echo:bool = True

class RedisSettings(BaseModel):
    host:str
    port:int = 6379
    decode_responses: bool = True

class AuthJWT(BaseModel):
    private_key_path:Path = BASE_DIR / 'core' / 'keys' / 'private.pem'
    public_key_path:Path = BASE_DIR / 'core' / 'keys' / 'public.pem'
    algorithm:str = 'RS256'
    access_token_expire_minutes:int = 15
    refresh_token_expire_days:int = 30
    
    @property
    def private_key(self):
        return self.private_key_path.read_text()
    
    @property
    def public_key(self):
        return self.public_key_path.read_text()
    
class Settings(BaseSettings):
    model_config = {
    "env_file": ".env",
    "env_nested_delimiter": "__",
    "extra": "ignore",
}

    db_settings: DBSettings
    redis_settings: RedisSettings
    auth_jwt:AuthJWT = AuthJWT()


settings = Settings()
