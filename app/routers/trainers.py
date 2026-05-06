from fastapi import APIRouter,Depends,HTTPException,status,Request
from ..core import db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from ..schemas import CreateTrainer,InfoAboutClient,TrainerRequestSchema,PatchTrainer,InfoAboutTrainer
from ..models import Trainer,Client,TrainerRequest
from ..core import hash_password,verify_password,encode_jwt,decode_jwt, require_active_trainer,check_email,apply_patch,delete_trainer,redis,rate_limit,register_universal,invalidate_trainers_cache
import json


router = APIRouter(prefix='/trainers',tags=['trainers'])



@router.get('/all_trainers',response_model=list[InfoAboutTrainer],dependencies=[Depends(rate_limit)])
async def all_trainers(db:AsyncSession = Depends(db_helper.current_session)):

    cache_key = "trainers:all"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    
    trainers = await db.scalars(select(Trainer).where(Trainer.is_active==True))
    result = trainers.all()
    
    data = [InfoAboutTrainer.model_validate(t).model_dump() for t in result]

    await redis.set(cache_key, json.dumps(data), ex=600)
    
    return data

@router.get('/deleted_trainers')
async def all_deleted_trainers(db:AsyncSession = Depends(db_helper.current_session)):
    trainers = await db.scalars(select(Trainer).where(Trainer.is_active==False))
    return trainers.all()


@router.post('/create_trainer',dependencies=[Depends(rate_limit),Depends(check_email)])
async def register_trainer(
                           trainer:CreateTrainer,
                           db:AsyncSession = Depends(db_helper.current_session)):
    
    new_trainer = await register_universal(trainer,Trainer,db)
    
    await invalidate_trainers_cache()
    
    return {"message":f'Trainer {new_trainer.id}: success registration'} 


@router.patch('/change_trainer',response_model=InfoAboutTrainer,dependencies=[Depends(check_email)])
async def change_client(new_data:PatchTrainer,
                        db:AsyncSession = Depends(db_helper.current_session),
                        user = Depends(require_active_trainer)
):

    await apply_patch(user,new_data,db)
    
    await db.commit()
    await invalidate_trainers_cache()
    return user


@router.get('/all_my_clients',response_model=list[InfoAboutClient])
async def show_clients(db:AsyncSession = Depends(db_helper.current_session),
                       user = Depends(require_active_trainer)):
    trainer = await db.scalar(select(Trainer).options(selectinload(Trainer.clients)).where(Trainer.id==user.id))
    return trainer.clients



@router.get('/show_requests',response_model=list[TrainerRequestSchema])
async def show_requests(db:AsyncSession = Depends(db_helper.current_session),
                        user = Depends(require_active_trainer)):
    requests = await db.scalars(select(TrainerRequest).options(selectinload(TrainerRequest.about_client)).where(TrainerRequest.trainer_id == user.id))
    return requests.all()

@router.post('/change_request')
async def change_request(status_request:str,
                         request_id:int,
                         db:AsyncSession = Depends(db_helper.current_session),
                         user = Depends(require_active_trainer)):
    
    request_status = await db.scalar(select(TrainerRequest)
                                     .options(selectinload(TrainerRequest.about_client))
                                     .where(TrainerRequest.id ==request_id,
                                            TrainerRequest.trainer_id==user.id,
                                            TrainerRequest.status =='pending'))
    if request_status is None:
        raise HTTPException(404,detail='Not status')
    
    if status_request == 'accept':
        request_status.status = 'accepted'
        request_status.about_client.trainer_id = user.id
        
    elif status_request == 'reject':
        request_status.status = 'rejected'
    else:
        raise HTTPException(status_code=400,detail='Invalid token')
    
    await db.commit()
    await invalidate_trainers_cache()
    return {'message':f'{request_status.status}'}


@router.delete('/delete_acc')
async def del_trainer(db:AsyncSession = Depends(db_helper.current_session),
                     user = Depends(require_active_trainer)):
    
    return await delete_trainer(db,user)
   

@router.delete('/all_del_test')
async def delete_all(db:AsyncSession = Depends(db_helper.current_session)):
    trainers = await db.scalars(select(Trainer).options(selectinload(Trainer.clients),selectinload(Trainer.trainer_request)))
    for trainer in trainers:
        
        for client in trainer.clients:
            client.trainer_id = None

        for req in trainer.trainer_request:
            await db.delete(req)

        await db.delete(trainer)
    
    await db.commit()
    await invalidate_trainers_cache()
    return trainers.all()