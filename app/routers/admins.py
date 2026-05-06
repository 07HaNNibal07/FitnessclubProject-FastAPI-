from fastapi import APIRouter,Depends,HTTPException,status,Request
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import settings,db_helper,hash_password,require_active_admin,check_email,apply_patch,delete_client,delete_trainer,rate_limit,register_universal,invalidate_trainers_cache
from ..schemas import CreateAdmin,AbstractPatch,InfoAboutAdmin,PatchClient
from ..models import Admin,Trainer,Client,TrainerRequest,AdminRequest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix='/admin',tags=['admin'])


        
@router.post('/create_admin',dependencies=[Depends(rate_limit),Depends(check_email)])
async def create_admin(
                       admin:CreateAdmin,
                       db:AsyncSession = Depends(db_helper.current_session)
):
    
    await register_universal(admin,Admin,db)

    return {"message":'success registration'} 


@router.get('/show_all_admins')
async def show(db:AsyncSession = Depends(db_helper.current_session)):
    admins = await db.scalars(select(Admin))
    return admins.all()



@router.patch('/change_admin',response_model=InfoAboutAdmin)
async def change_client(new_data:AbstractPatch,
                        db:AsyncSession = Depends(db_helper.current_session),
                        user = Depends(require_active_admin)
):

    await apply_patch(user,new_data,db)
    
    await db.commit()
    return user

@router.get('/show_requests_to_trainers',dependencies=[Depends(require_active_admin)])
async def show_requests(db:AsyncSession = Depends(db_helper.current_session)
):
    request = await db.scalars(select(TrainerRequest))
    return request.all()



@router.get('/show_requests_to_admins',dependencies=[Depends(require_active_admin)])
async def show_my_requests(
    db:AsyncSession = Depends(db_helper.current_session),
):
    requests = await db.scalars(select(AdminRequest))
    
    return requests.all()

async def check_request(request_id:int,db:AsyncSession = Depends(db_helper.current_session)):
    data = await db.scalar(select(AdminRequest).options(selectinload(AdminRequest.about_client)).where(AdminRequest.id==request_id))
    if data is None or data.status == 'data_changed':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='There is no such request')

    return data
    
@router.patch('/make_changes',dependencies=[Depends(require_active_admin)])
async def make_changes(
                       new_data:PatchClient,
                       data:AdminRequest = Depends(check_request),
                       db:AsyncSession = Depends(db_helper.current_session)
):

    client = data.about_client
    
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found')
    for key,val in new_data.model_dump(exclude_unset=True).items():
        if key not in ['password','email','number','trainer_id']:
            setattr(client,key,val)
            
    data.status = 'data_changed'
    
    await db.commit()
    return {'message':'data changed'}
    

@router.delete('/delete_user_or_trainer',dependencies=[Depends(require_active_admin)])
async def delete_user_or_trainer(user_email:str,
                                 db:AsyncSession = Depends(db_helper.current_session),
):
    
    for Model in [Client,Trainer]:
        find_user = await db.scalar(select(Model).where(Model.email==user_email))
        
        if Model == Client and find_user:
            return await delete_client(db,find_user)
        
        elif Model == Trainer and find_user:
            return await delete_trainer(db,find_user)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        

@router.delete('/test_delete{admin_id}')
async def del_client(admin_id:int,
                     db:AsyncSession = Depends(db_helper.current_session),
                     ):

    admin = await db.get(Admin,admin_id)
    await db.delete(admin)
    await db.commit()
    return {"message": "User deleted successfully"}        

