from database import engine
from models import BaseModel

BaseModel.metadata.create_all(bind=engine)
