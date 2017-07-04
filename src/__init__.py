from .core import hmm
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


def connect(user, password, db, host='localhost', port=5432):
    """Returns a engine and a metadata object"""
    # We connect with the help of the PostgreSQL URL
    # postgresql://postgres:123456@localhost:5432/TrainingAndFoodTracker
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    engine = create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = MetaData(bind=engine, reflect=True)

    return engine, meta

engine, meta = connect("postgres", "123456", "TrainingAndFoodTracker")
Session = sessionmaker(bind=engine)
# print(Session)


