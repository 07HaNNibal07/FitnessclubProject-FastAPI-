from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException,Depends,APIRouter,Form,status,Request
from .auth import hash_password,verify_password,encode_jwt,decode_jwt,create_refresh_token,create_access_token
from fastapi.security import OAuth2PasswordBearer
from ..models import Client,Trainer,Admin
from .db_dep import db_helper
from .redis import rate_limit

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

MODEL_MAP = {
    "client": Client,
    "trainer": Trainer,
    "admin": Admin
}

def get_current_user(require_role:str):
    async def get_requaire_role(token = Depends(oauth2_scheme),db: AsyncSession = Depends(db_helper.current_session)):
        
        payload = decode_jwt(token=token)
        token_type = payload.get("type")

        if token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        role = payload.get('role')
        if role != require_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        model = MODEL_MAP.get(role)
        user_id = payload.get('sub')
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        user = await db.get(model,int(payload['sub']))
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        return user
        
    return get_requaire_role


def require_active_user(role: str):
    get_user = get_current_user(role)

    async def dependency(user=Depends(get_user)):
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return user

    return dependency

require_active_client = require_active_user('client')
require_active_trainer = require_active_user('trainer')
require_active_admin = require_active_user('admin')

def get_token(plain_password,user,role):
    if user is not None:
        if verify_password(plain_password,user.password):
            payload = { 'sub':str(user.id),
                        'email':user.email,
                        'role':role}
        
            return {
                "access_token" : create_access_token(payload=payload),
                'refresh_token': create_refresh_token(payload=payload),
                "token_type": "bearer"
            }


@router.post('/login',dependencies=[Depends(rate_limit)])
async def login_user(
                     username:str = Form(...,description='Введите почту'),
                     password:str = Form(...,description='Введите пароль'),
                     db:AsyncSession = Depends(db_helper.current_session),
):
    
    
    for role,Model in MODEL_MAP.items():
        user = await db.scalar(select(Model).where(Model.email==username))
        if user is not None:
            token = get_token(password,user,role)
            if token:
                return token

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Wrong email or password')


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    payload = decode_jwt(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid token")

    new_access = create_access_token(payload)

    return {"access_token": new_access}


MODELS = [Client, Trainer, Admin]

async def check_email(request:Request,db:AsyncSession = Depends(db_helper.current_session)):
    
    body = await request.json()
    email = body.get('email')
    
    for model in MODELS:
        existing = await db.scalar(select(model).where(model.email == email))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    

# async def invalidate_trainers_cache():
#     await redis.delete("all_trainers")
    






