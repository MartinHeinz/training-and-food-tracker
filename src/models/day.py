from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from src import engine

Base = declarative_base()


class Day(Base):
    __tablename__ = 'day'
    
    id = Column(Integer, primary_key=True)
    body_composition = relationship("BodyComposition", uselist=False, back_populates="day")
    date = Column(Date)
    target_cal = Column(postgresql.INT4RANGE, nullable=False)
    target_carbs = Column(postgresql.INT4RANGE)
    target_protein = Column(postgresql.INT4RANGE)
    target_fat = Column(postgresql.INT4RANGE)
    target_fiber = Column(postgresql.INT4RANGE)
    

class BodyComposition(Base):
    __tablename__ = 'body_composition'
    
    id = Column(Integer, primary_key=True)
    day_id = Column(Integer, ForeignKey('day.id'))
    day = relationship("Day", back_populates="body_composition")
    body_fat = Column(Numeric(precision=3, scale=2))
    chest = Column(Numeric(precision=3, scale=2))
    arm = Column(Numeric(precision=3, scale=2))
    waist = Column(Numeric(precision=3, scale=2))
    belly = Column(Numeric(precision=3, scale=2))
    thigh = Column(Numeric(precision=3, scale=2))
    calf = Column(Numeric(precision=3, scale=2))
    forearm = Column(Numeric(precision=3, scale=2))
    weight = Column(Numeric(precision=3, scale=2))

Base.metadata.create_all(engine)
