from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase
from sqlalchemy.orm import sessionmaker

Base = declarative_base(cls=RepresentableBase)


class DataAccessLayer:
    def __init__(self, user, password, db, host='localhost', port=5432):
        # postgresql://postgres:123456@localhost:5432/TrainingAndFoodTracker
        url = 'postgresql://{}:{}@{}:{}/{}'
        self.engine = None
        self.Session = None
        self.session = None
        self.conn_string = url.format(user, password, host, port, db)

    def connect(self):
        self.engine = create_engine(self.conn_string)
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

dal = DataAccessLayer("postgres", "123456", "TrainingAndFoodTracker")

