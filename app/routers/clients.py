from fastapi import APIRouter,Depends,HTTPException,Form,status,Request
from ..schemas import CreateUser,PatchClient,InfoAboutTrainer,InfoAboutClient,ClientRequestSchema,InfoAboutClient
from ..core.db_dep import db_helper
from ..core.auth import hash_password, verify_password, encode_jwt, decode_jwt
from ..core.utils import require_active_client, check_email
from ..core.crud import apply_patch, delete_client, register_universal
from ..core.redis import redis, rate_limit
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import selectinload
from ..models import Client,Trainer,TrainerRequest,AdminRequest
from datetime import datetime
import logging



logger = logging.getLogger(__name__)

router = APIRouter(prefix='/clients',tags=['clients'])

@router.get('/all_clients',response_model=list[InfoAboutClient])
async def all_clients(db:AsyncSession = Depends(db_helper.current_session)):
    client = await db.scalars(select(Client).where(Client.is_active))
    return client.all()

@router.get('/deleted_clients')
async def all_deleted_trainers(db:AsyncSession = Depends(db_helper.current_session)):
    trainers = await db.scalars(select(Client).where(Client.is_active==False))
    return trainers.all()


@router.get('/get{client_id}',response_model=InfoAboutClient)
async def get_client(client_id:int,
                     db:AsyncSession = Depends(db_helper.current_session)):
    client = await db.get(Client, client_id)
    return client


@router.post('/register_client',dependencies=[
    Depends(rate_limit),
    Depends(check_email)
    ])
async def reg_client(user:CreateUser,
                     db:AsyncSession = Depends(db_helper.current_session)
):
    
    client_data = await register_universal(user,Client,db)
    
    logging.info(f"CLIENT {client_data.id} REGISTERED")
    return {"message":'success registration'}

@router.get('/show_trainer',response_model=list[InfoAboutTrainer])
async def show_trainers(db:AsyncSession = Depends(db_helper.current_session),
                        user = Depends(require_active_client)):

    trainers = await db.scalars(select(Trainer).where(Trainer.is_active==True))
    return trainers.all()

@router.post('/choose_trainer')
async def choose_trainer (trainer_id:int,
                          db:AsyncSession = Depends(db_helper.current_session),
                          user = Depends(require_active_client)):
    
    check_requests = await db.scalar(select(TrainerRequest).where(and_(TrainerRequest.client_id==user.id,TrainerRequest.trainer_id == trainer_id)))
    if check_requests:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Request is already sent')
    
    new_request = TrainerRequest(
        client_id = user.id,
        trainer_id = trainer_id,
        status = 'pending'
    )
    
    db.add(new_request)
    
    logging.info(f"CLIENT {user.id} SENT REQUEST TO {trainer_id}")
    
    await db.commit()
    return {'message':'request sent'}

@router.post('/put_request_to_admin')
async def put_request(ask:str,
                      db:AsyncSession = Depends(db_helper.current_session),
                      user = Depends(require_active_client)):
    
    key = f"user:{user.id}:admin_requests"
    count = await redis.get(key)
    if count and int(count) >= 3:
        raise HTTPException(429, "Too many requests")
    await redis.incr(key)
    await redis.expire(key, 60)
    
    db_ask = AdminRequest(
        description = ask,
        status = 'pending',
        client_id = user.id
    )
    db.add(db_ask)
    logging.info(f"CLIENT {user.id} SENT REQUEST TO ADMINS")
    await db.commit()
    return {'message':'request sent'}

@router.get('/show_my_requests',response_model=list[ClientRequestSchema])
async def show_my_requests(db:AsyncSession = Depends(db_helper.current_session),
                           user = Depends(require_active_client)):
    my_requests = await db.scalars(select(TrainerRequest).options(selectinload(TrainerRequest.about_trainer)).where(TrainerRequest.client_id ==user.id))
    return my_requests.all()

@router.get('/my_trainer',response_model=InfoAboutTrainer)
async def show_trainer(db:AsyncSession = Depends(db_helper.current_session),
                       user = Depends(require_active_client)):
    
    client = await db.scalar(select(Client).options(selectinload(Client.trainer)).where(Client.id == user.get('sub')))
    
    try:
        return client.trainer
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@router.get('/show_my_admin_requests')
async def show_my_admin_requests(
                           db:AsyncSession = Depends(db_helper.current_session),
                           user = Depends(require_active_client)
):
    my_requests = await db.scalars(select(AdminRequest).where(AdminRequest.client_id==user.id))
    return my_requests.all()

@router.get("/protected",response_model=InfoAboutClient)
async def protected_route(token: str = Depends(require_active_client)):
    return token
        
    

@router.patch('/change_client',response_model=InfoAboutClient,dependencies=[Depends(check_email)])
async def change_client(new_data:PatchClient,
                        db:AsyncSession = Depends(db_helper.current_session),
                        user = Depends(require_active_client)
):

    await apply_patch(user,new_data,db)
    logging.info(f"CLIENT {user.id} CHANGED DATA | TIME: {datetime.utcnow()}")
    await db.commit()
    return user


@router.delete('/delete_acc')
async def del_client(db:AsyncSession = Depends(db_helper.current_session),
                     user = Depends(require_active_client)):
    logging.info(f"CLIENT {user.id} DELETED | TIME: {datetime.utcnow()}")
    return await delete_client(db,user)


@router.delete('/all_del_test')
async def delete_all(db:AsyncSession = Depends(db_helper.current_session)):
    clients = await db.scalars(select(Client).options(selectinload(Client.to_admin_requests),selectinload(Client.client_request)))
    
    for client in clients:

        for req in client.to_admin_requests:
            await db.delete(req)
            
        for req in client.client_request:
            await db.delete(req)
            
        await db.delete(client)
    await db.commit()
    return {"message": "all clients deleted"}
    