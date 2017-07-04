from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Numeric, String, Text, Boolean, Time, Interval
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
# from src import engine

Base = declarative_base()

exercise_equipment_table = Table('exercise_equipment', Base.metadata,
                                 Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                 Column('exercise_id', Integer, ForeignKey('exercise.id'))
                                 )

exercise_tag_table = Table('exercise_tag', Base.metadata,
                           Column('tag_id', Integer, ForeignKey('tag.id')),
                           Column('exercise_id', Integer, ForeignKey('exercise.id'))
                           )

training_template_exercise_table = Table('training_template_exercise', Base.metadata,
                                         Column('training_template_id', Integer, ForeignKey('training_template.id')),
                                         Column('exercise_id', Integer, ForeignKey('exercise.id'))
                                         )


class Exercise(Base):
    __tablename__ = 'exercise'

    id = Column(Integer, primary_key=True)
    weight_id = Column(Integer, ForeignKey('weight.id'))
    weight = relationship("Weight", back_populates="exercise")
    name = Column(String)
    tempo = Column(String)
    pause = Column(postgresql.INT4RANGE)
    set_range = Column(postgresql.INT4RANGE)
    rep_range = Column(postgresql.INT4RANGE)
    notes = Column(Text)
    equipment = relationship(
        "Equipment",
        secondary=exercise_equipment_table,
        back_populates="exercises")
    tags = relationship(
        "Tag",
        secondary=exercise_tag_table,
        back_populates="exercises")
    training_templates = relationship(
        "TrainingTemplate",
        secondary=training_template_exercise_table,
        back_populates="exercises")
    training_session_exercises = relationship("TrainingSessionExercise", back_populates="exercise")
    goal = relationship("Goal", uselist=False, back_populates="exercise")


class Weight(Base):
    __tablename__ = 'weight'

    id = Column(Integer, primary_key=True)
    exercise = relationship("Exercise", back_populates="weight", uselist=False)
    RM = Column(Integer)
    percentage_range = Column(postgresql.INT4RANGE)
    kilogram = Column(Numeric(precision=3, scale=2))
    BW = Column(Boolean)
    band = Column(String)


class Equipment(Base):
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    exercises = relationship(
        "Exercise",
        secondary=exercise_equipment_table,
        back_populates="equipment")


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    exercises = relationship(
        "Exercise",
        secondary=exercise_tag_table,
        back_populates="tags")


class Set(Base):
    __tablename__ = 'set'

    id = Column(Integer, primary_key=True)
    reps = Column(Integer)
    weight = Column(Numeric(precision=3, scale=2))
    is_PR = Column(Boolean)
    training_session_exercise_id = Column(Integer, ForeignKey('training_session_exercise.id'))


class TrainingSession(Base):
    __tablename__ = 'training_session'

    id = Column(Integer, primary_key=True)
    start = Column(Time)
    end = Column(Time)
    training_template_id = Column(Integer, ForeignKey('training_template.id'))
    training_template = relationship("TrainingTemplate", back_populates="training_sessions")
    training_session_exercises = relationship("TrainingSessionExercise", back_populates="training_session")


class TrainingSessionExercise(Base):
    __tablename__ = 'training_session_exercise'

    id = Column(Integer, primary_key=True)
    training_session_id = Column(Integer, ForeignKey('training_session.id'))
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    exercise = relationship("Exercise", back_populates="training_session_exercises")
    is_optional = Column(Boolean)
    prev = relationship("training_session_exercise",
                        uselist=False,
                        remote_side=[id],
                        backref=backref("superset_with", uselist=False))
    superset_with = relationship("training_session_exercise",
                                 uselist=False,
                                 backref=backref("prev", uselist=False))
    prev_training_session_exercise_id = Column(Integer, ForeignKey('training_session_exercise.id'))
    # might be wrong: https://stackoverflow.com/questions/12872873/one-to-one-self-relationship-in-sqlalchemy
    pause = Column(Interval)
    sets = relationship("Set")
    training_session = relationship("TrainingSession", back_populates="training_session_exercises")


class TrainingTemplate(Base):
    __tablename__ = 'training_template'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    training_sessions = relationship("TrainingSession", back_populates="training_template")
    phase_id = Column(Integer, ForeignKey('phase.id'))
    phase = relationship("Phase", back_populates="training_templates")
    exercises = relationship(
        "Exercise",
        secondary=training_template_exercise_table,
        back_populates="training_templates")


class Phase(Base):
    __tablename__ = 'phase'

    id = Column(Integer, primary_key=True)
    training_templates = relationship("TrainingTemplate", back_populates="phase")
    training_plan_id = Column(Integer, ForeignKey('training_plan.id'))
    training_plan = relationship("TrainingPlan", back_populates="phases")


class TrainingPlan(Base):
    __tablename__ = 'training_plan'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    phases = relationship("Phase", back_populates="training_plan")
    training_program_history = relationship("TrainingPlanHistory", back_populates="training_plan")
    goals = relationship("Goal", back_populates="training_plan")


class TrainingPlanHistory(Base):
    __tablename__ = 'training_plan_history'

    id = Column(Integer, primary_key=True)
    training_plan_id = Column(Integer, ForeignKey('training_plan.id'))
    training_plan = relationship("TrainingPlan", back_populates="training_program_history")
    start = Column(Date)
    end = Column(Date)


class Goal(Base):
    __tablename__ = 'goal'

    id = Column(Integer, primary_key=True)
    is_main = Column(Boolean)
    notes = Column(Text)
    training_plan_id = Column(Integer, ForeignKey('training_plan.id'))
    training_plan = relationship("TrainingPlan", back_populates="goals")
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    exercise = relationship("Exercise", back_populates="goal")
    prev = relationship("goal",
                        uselist=False,
                        remote_side=[id],
                        backref=backref("next_partial", uselist=False))
    next_partial = relationship("training_session_exercise",
                                uselist=False,
                                backref=backref("prev", uselist=False))
    prev_goal_id = Column(Integer, ForeignKey('goal.id'))
