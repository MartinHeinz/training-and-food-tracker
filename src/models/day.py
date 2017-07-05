from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Numeric, String, Text, Boolean, Interval, Time
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import postgresql
from src.models.base import Base
# from src import engine

# from src.models.training import *


class Day(Base):
    __tablename__ = 'day'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    body_composition = relationship("BodyComposition", uselist=False, back_populates="day")
    date = Column(Date)
    target_cal = Column(postgresql.INT4RANGE, nullable=False)
    target_carbs = Column(postgresql.INT4RANGE)
    target_protein = Column(postgresql.INT4RANGE)
    target_fat = Column(postgresql.INT4RANGE)
    target_fiber = Column(postgresql.INT4RANGE)
    training_session_id = Column(Integer, ForeignKey('training_session.id'))
    training_session = relationship("TrainingSession", uselist=False, back_populates="day")
    meals = relationship("Meal", back_populates="day")


class BodyComposition(Base):
    __tablename__ = 'body_composition'
    __table_args__ = {'extend_existing': True}

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

