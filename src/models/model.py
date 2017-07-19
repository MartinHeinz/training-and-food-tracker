from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Numeric, String, Text, Boolean, Time, and_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import postgresql
from src.models.base import MixinGetByName, transaction
from src import Base
from src.models.util import sort_to_match


recipe_tag_table = Table('recipe_tag', Base.metadata,
                         Column("recipe_id", Integer, ForeignKey('recipe.id')),
                         Column('tag_id', Integer, ForeignKey('tag.id')),
                         extend_existing=True
                         )

exercise_equipment_table = Table('exercise_equipment', Base.metadata,
                                 Column('equipment_id', Integer, ForeignKey('equipment.id')),
                                 Column('exercise_id', Integer, ForeignKey('exercise.id')),
                                 extend_existing=True
                                 )

exercise_tag_table = Table('exercise_tag', Base.metadata,
                           Column('tag_id', Integer, ForeignKey('tag.id')),
                           Column('exercise_id', Integer, ForeignKey('exercise.id')),
                           extend_existing=True
                           )

# training_template_exercise_table = Table('training_template_exercise', Base.metadata,
#                                          Column('training_template_id', Integer, ForeignKey('training_template.id')),
#                                          Column('exercise_id', Integer, ForeignKey('exercise.id')),
#                                          extend_existing=True
#                                          )


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
    target_fibre = Column(postgresql.INT4RANGE)
    training_session_id = Column(Integer, ForeignKey('training_session.id'))
    training_session = relationship("TrainingSession", uselist=False, back_populates="day")
    meals = relationship("Meal", back_populates="day")

    @classmethod
    def get_by_date(cls, session, date):
        return session.query(cls).filter(cls.date == date).scalar()


class BodyComposition(Base):
    __tablename__ = 'body_composition'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    day_id = Column(Integer, ForeignKey('day.id'))
    day = relationship("Day", back_populates="body_composition")
    body_fat = Column(Numeric(precision=5, scale=2))
    chest = Column(Numeric(precision=5, scale=2))
    arm = Column(Numeric(precision=5, scale=2))
    waist = Column(Numeric(precision=5, scale=2))
    belly = Column(Numeric(precision=5, scale=2))
    thigh = Column(Numeric(precision=5, scale=2))
    calf = Column(Numeric(precision=5, scale=2))
    forearm = Column(Numeric(precision=5, scale=2))
    weight = Column(Numeric(precision=5, scale=2))


class FoodMeasurement(Base):
    __tablename__ = 'food_measurement'
    __table_args__ = {'extend_existing': True}
    food_id = Column(Integer, ForeignKey('food.id'), primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurement.id'), primary_key=True)
    grams = Column(Integer)
    measurement = relationship("Measurement", back_populates="foods")
    food = relationship("Food", back_populates="measurements")


class FoodRecipe(Base):
    __tablename__ = 'food_recipe'
    __table_args__ = {'extend_existing': True}
    food_id = Column(Integer, ForeignKey('food.id'), primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True)
    amount = Column(Integer)
    food = relationship("Food", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="foods")


class MealRecipe(Base):
    __tablename__ = 'meal_recipe'
    __table_args__ = {'extend_existing': True}
    meal_id = Column(Integer, ForeignKey('meal.id'), primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'), primary_key=True)
    amount = Column(Numeric(precision=5, scale=2))
    meal = relationship("Meal", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="meals")


class MealFood(Base):
    __tablename__ = 'meal_food'
    __table_args__ = {'extend_existing': True}
    meal_id = Column(Integer, ForeignKey('meal.id'), primary_key=True)
    food_id = Column(Integer, ForeignKey('food.id'), primary_key=True)
    amount = Column(Integer)
    meal = relationship("Meal", back_populates="foods")
    food = relationship("Food", back_populates="meals")


class Food(MixinGetByName, Base):
    __tablename__ = 'food'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    cal = Column(Integer)
    protein = Column(Integer)
    carbs = Column(Integer)
    fat = Column(Integer)
    fibre = Column(Integer)
    measurements = relationship("FoodMeasurement", back_populates="food")
    meals = relationship("MealFood", back_populates="food")
    recipes = relationship("FoodRecipe", back_populates="food")


class Measurement(MixinGetByName, Base):
    __tablename__ = 'measurement'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    foods = relationship("FoodMeasurement", back_populates="measurement")


class Meal(Base):
    __tablename__ = 'meal'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    foods = relationship("MealFood", back_populates="meal")
    recipes = relationship("MealRecipe", back_populates="meal")
    day_id = Column(Integer, ForeignKey('day.id'))
    day = relationship("Day", back_populates="meals")


class Recipe(MixinGetByName, Base):
    __tablename__ = 'recipe'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    serving_size = Column(Numeric(precision=5, scale=2))
    notes = Column(Text)
    foods = relationship("FoodRecipe", back_populates="recipe")
    meals = relationship("MealRecipe", back_populates="recipe")
    tags = relationship(
        "Tag",
        secondary=recipe_tag_table,
        back_populates="recipes")


class Exercise(MixinGetByName, Base):
    __tablename__ = 'exercise'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    weight_id = Column(Integer, ForeignKey('weight.id'))
    weight = relationship("Weight", back_populates="exercise")
    tempo = Column(String)
    # pause = Column(postgresql.INT4RANGE)
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
    training_template_exercises = relationship("TrainingTemplateExercise", back_populates="exercise")
    training_session_exercises = relationship("TrainingSessionExercise", back_populates="exercise")
    goal = relationship("Goal", uselist=False, back_populates="exercise")

    @classmethod
    def get_by_tag(cls, session, tags):
        return session.query(cls).join(cls.tags).filter(Tag.name.in_(tags)).all()


class Weight(Base):
    __tablename__ = 'weight'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    exercise = relationship("Exercise", back_populates="weight", uselist=False)
    RM = Column(Integer)
    percentage_range = Column(postgresql.NUMRANGE)
    kilogram = Column(postgresql.NUMRANGE)
    BW = Column(Boolean)
    band = Column(String)


class Equipment(Base):
    __tablename__ = 'equipment'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    exercises = relationship(
        "Exercise",
        secondary=exercise_equipment_table,
        back_populates="equipment")


class Tag(Base):
    __tablename__ = 'tag'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)  # exercise/recipe
    description = Column(Text)
    exercises = relationship(
        "Exercise",
        secondary=exercise_tag_table,
        back_populates="tags")
    recipes = relationship(
        "Recipe",
        secondary=recipe_tag_table,
        back_populates="tags")


class Set(Base):
    __tablename__ = 'set'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    reps = Column(Integer)
    weight = Column(Numeric(precision=5, scale=2))
    is_PR = Column(Boolean)
    is_AMRAP = Column(Boolean)
    training_session_exercise_id = Column(Integer, ForeignKey('training_session_exercise.id'))


class TrainingSession(Base):
    __tablename__ = 'training_session'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    start = Column(Time)
    end = Column(Time)
    training_template_id = Column(Integer, ForeignKey('training_template.id'))
    training_template = relationship("TrainingTemplate", back_populates="training_sessions")
    day = relationship("Day", back_populates="training_session", uselist=False)
    training_session_exercises = relationship("TrainingSessionExercise", back_populates="training_session")


class TrainingSessionExercise(Base):
    __tablename__ = 'training_session_exercise'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    training_session_id = Column(Integer, ForeignKey('training_session.id'))
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    exercise = relationship("Exercise", back_populates="training_session_exercises")
    training_session = relationship("TrainingSession", back_populates="training_session_exercises")
    is_optional = Column(Boolean)
    superset_with = relationship("TrainingSessionExercise",
                                 uselist=False,
                                 backref=backref("prev", uselist=False, remote_side=[id]))
    prev_training_session_exercise_id = Column(Integer, ForeignKey('training_session_exercise.id'))
    # might be wrong: https://stackoverflow.com/questions/12872873/one-to-one-self-relationship-in-sqlalchemy
    pause = Column(postgresql.INT4RANGE)
    sets = relationship("Set")

    #  TODO: TEST
    @classmethod
    def create_superset(cls, session, exercise_ids, session_id):
        training_session = session.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        training_session_exercises = [TrainingSessionExercise() for _ in range(len(exercise_ids))]
        exercises = session.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
        exercises = sort_to_match(exercise_ids, exercises)
        for i, ex in enumerate(exercises):
            training_session_exercises[i].exercise = ex
            training_session_exercises[i].sets = [Set(reps=ex.rep_range.upper) for _ in range(ex.set_range.upper)]
            if i == 0:
                training_session.training_session_exercises.append(training_session_exercises[i])
            if i != len(exercises)-1:
                training_session_exercises[i].superset_with = training_session_exercises[i+1]
            # session.add(training_session_exercises[i])
        return training_session_exercises


class TrainingTemplate(Base):
    __tablename__ = 'training_template'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    training_sessions = relationship("TrainingSession", back_populates="training_template")
    phase_id = Column(Integer, ForeignKey('phase.id'))
    phase = relationship("Phase", back_populates="training_templates")
    training_template_exercises = relationship("TrainingTemplateExercise", back_populates="training_template")
    description = Column(Text)


class TrainingTemplateExercise(Base):
    __tablename__ = 'training_template_exercise'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    training_template_id = Column(Integer, ForeignKey('training_template.id'))
    is_optional = Column(Boolean)
    pause = Column(postgresql.INT4RANGE)
    superset_with = relationship("TrainingTemplateExercise",
                                 uselist=False,
                                 backref=backref("prev", uselist=False, remote_side=[id]))
    prev_training_template_exercise_id = Column(Integer, ForeignKey('training_template_exercise.id'))
    exercise = relationship("Exercise", back_populates="training_template_exercises")
    training_template = relationship("TrainingTemplate", back_populates="training_template_exercises")

    #  TODO: TEST
    @classmethod
    def create_superset(cls, session, exercise_ids, template_id):
        template = session.query(TrainingTemplate).filter(TrainingTemplate.id == template_id).first()
        training_template_exercises = [TrainingTemplateExercise() for _ in range(len(exercise_ids))]
        exercises = session.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
        exercises = sort_to_match(exercise_ids, exercises)
        for i, ex in enumerate(exercises):
            training_template_exercises[i].exercise = ex
            if i == 0:
                template.training_template_exercises.append(training_template_exercises[i])
            if i != len(exercises)-1:
                training_template_exercises[i].superset_with = training_template_exercises[i+1]
            # session.add(training_template_exercises[i])
        return training_template_exercises


class Phase(Base):
    __tablename__ = 'phase'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    training_templates = relationship("TrainingTemplate", back_populates="phase")
    training_plan_id = Column(Integer, ForeignKey('training_plan.id'))
    training_plan = relationship("TrainingPlan", back_populates="phases")
    name = Column(String)
    length = Column(postgresql.INT4RANGE)
    description = Column(Text)


class TrainingPlan(MixinGetByName, Base):
    __tablename__ = 'training_plan'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    # name = Column(String)
    description = Column(Text)
    phases = relationship("Phase", back_populates="training_plan")
    training_plan_history = relationship("TrainingPlanHistory", back_populates="training_plan")
    # goals = relationship("Goal", back_populates="training_plan")

    @classmethod  # TODO test
    def get_current(cls, session):
        return session.query(cls).join(cls.training_plan_history).filter(
            and_(TrainingPlanHistory.start is None, TrainingPlanHistory.end is None)
        ).scalar()


class TrainingPlanHistory(Base):
    __tablename__ = 'training_plan_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    training_plan_id = Column(Integer, ForeignKey('training_plan.id'))
    training_plan = relationship("TrainingPlan", back_populates="training_plan_history")
    goals = relationship("Goal", back_populates="training_plan_history")
    start = Column(Date)
    end = Column(Date)


class Goal(MixinGetByName, Base):
    __tablename__ = 'goal'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    is_main = Column(Boolean)
    notes = Column(Text)
    date = Column(Date)
    kilogram = Column(Numeric(precision=5, scale=2))
    reps = Column(Integer)
    training_plan_history_id = Column(Integer, ForeignKey('training_plan_history.id'))
    training_plan_history = relationship("TrainingPlanHistory", back_populates="goals")
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    exercise = relationship("Exercise", back_populates="goal")
    next_partial = relationship("Goal",
                                uselist=False,
                                backref=backref("prev", uselist=False, remote_side=[id]))
    prev_goal_id = Column(Integer, ForeignKey('goal.id'))

    @classmethod
    def create_goal(cls, session, size):
        # TODO
        return







