from pydantic import BaseModel,ConfigDict
from .trainers import InfoAboutTrainer
from .clients import InfoAboutClient


class ClientRequestSchema(BaseModel):
    id: int
    trainer_id: int
    client_id: int
    status: str
    about_trainer: InfoAboutTrainer
    
    model_config = ConfigDict(from_attributes=True)
    
class TrainerRequestSchema(BaseModel):
    id: int
    trainer_id: int
    client_id: int
    status: str
    about_client: InfoAboutClient
    model_config = ConfigDict(from_attributes=True)