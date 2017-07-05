from src import engine
from src.models.base import Base
from src.models.day import *
from src.models.food import *
from src.models.training import *

# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
