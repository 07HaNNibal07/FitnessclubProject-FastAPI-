from sqlalchemy.orm import selectinload
from fastapi import HTTPException,status
from ..models import Trainer,Client,Admin
from sqlalchemy import select
from .utils import check_email
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import decode_jwt,encode_jwt,hash_password,verify_password
from .redis import invalidate_trainers_cache


async def delete_trainer(db,user):
    trainer = await db.scalar(select(Trainer).options(selectinload(Trainer.clients),selectinload(Trainer.trainer_request)).where(Trainer.id==user.id))
    if trainer.is_active ==False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    for client in trainer.clients:
        client.trainer_id = None

    for req in trainer.trainer_request:
            await db.delete(req)
    trainer.is_active = False
    
    await invalidate_trainers_cache()
    await db.commit()
    return {"message": f"Trainer {trainer.id}: deleted successfully"}


async def delete_client(db,user):
    client = await db.scalar(select(Client).options(selectinload(Client.to_admin_requests),selectinload(Client.client_request)).where(Client.id==user.id))
    
    if client.is_active ==False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    for req in client.to_admin_requests:
        await db.delete(req)
        
    for req in client.client_request:
        await db.delete(req)
        
    client.trainer_id = None
    client.is_active = False
    await db.commit()
    
    return {"message": f"Client {client.id}: deleted successfully"}

async def register_universal(user,Model,db:AsyncSession):
            
        db_user = user.model_dump()
        db_user['password'] = hash_password(user.password)
        
        if db_user.get("trainer_id") == 0:
            db_user["trainer_id"] = None
        
        new_db_user = Model(**db_user)
        
        db.add(new_db_user)
        await db.commit()
        await db.refresh(new_db_user)
        return new_db_user


async def apply_patch(user, data, db):
    for key, val in data.model_dump(exclude_unset=True).items():
        if key == "password":
            val = hash_password(val)

        setattr(user, key, val)