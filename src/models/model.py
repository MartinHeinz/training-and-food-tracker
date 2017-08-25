from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Numeric, String, Text, Boolean, Time, and_, or_, cast
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


class Day(Base):
    __tablename__ = 'day'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    body_composition = relationship("BodyComposition", uselist=False, back_populates="day")
    date = Column(Date)
    target_cal = Column(postgresql.INT4RANGE)
    target_carbs = Column(postgresql.INT4RANGE)
    target_protein = Column(postgresql.INT4RANGE)
    target_fat = Column(postgresql.INT4RANGE)
    target_fibre = Column(postgresql.INT4RANGE)
    training_id = Column(Integer, ForeignKey('training.id'))
    training = relationship("Training", uselist=False, back_populates="day")
    meals = relationship("Meal", back_populates="day")

    @classmethod
    def get_by_date(cls, session, date):
        return session.query(cls).filter(cls.date == date).scalar()

    @classmethod
    def get_most_recent(cls, session):
        return session.query(cls).order_by(cls.date.desc()).first()


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


# class FoodMeasurement(Base):
#     __tablename__ = 'food_measurement'
#     __table_args__ = {'extend_existing': True}
#     food_id = Column(Integer, ForeignKey('food.id'), primary_key=True)
#     measurement_id = Column(Integer, ForeignKey('measurement.id'), primary_key=True)
#     grams = Column(Integer)
#     measurement = relationship("Measurement", back_populates="foods")
#     food = relationship("Food", back_populates="measurements")


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
    amount = Column(Numeric(precision=5, scale=2))
    meal = relationship("Meal", back_populates="foods")
    food = relationship("Food", back_populates="meals")


class Food(MixinGetByName, Base):
    __tablename__ = 'food'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    cal = Column(Numeric(precision=5, scale=2))
    protein = Column(Numeric(precision=5, scale=2))
    carbs = Column(Numeric(precision=5, scale=2))
    fat = Column(Numeric(precision=5, scale=2))
    fibre = Column(Numeric(precision=5, scale=2))
    brand = Column(String)
    measurements = relationship("Measurement", back_populates="food")  # TODO test
    meals = relationship("MealFood", back_populates="food")
    recipes = relationship("FoodRecipe", back_populates="food")


class Measurement(MixinGetByName, Base):
    __tablename__ = 'measurement'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    food = relationship("Food", back_populates="measurements")  # TODO test


class Meal(MixinGetByName, Base):
    __tablename__ = 'meal'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    foods = relationship("MealFood", back_populates="meal")
    recipes = relationship("MealRecipe", back_populates="meal")
    day_id = Column(Integer, ForeignKey('day.id'))
    day = relationship("Day", back_populates="meals")

    def add_food(self, food, amount):  # TODO test
        meal_food = MealFood(amount=amount)
        meal_food.food = food
        if self.foods is None:
            self.foods = [meal_food]
        else:
            self.foods.append(meal_food)

    def add_recipe(self, recipe, amount):  # TODO test
        meal_recipe = MealRecipe(amount=amount)
        meal_recipe.food = recipe
        if self.recipes is None:
            self.recipes = [meal_recipe]
        else:
            self.recipes.append(meal_recipe)


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

    def add_food(self, food, amount):  # TODO test
        food_recipe = FoodRecipe(amount=amount)
        food_recipe.food = food
        if self.foods is None:
            self.foods = [food_recipe]
        else:
            self.foods.append(food_recipe)


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
    training_exercises = relationship("TrainingExercise", back_populates="exercise")
    goal = relationship("Goal", uselist=False, back_populates="exercise")

    def get_field_secondary_text(self):
        if self.set_range.lower is None:
            sets = "None"
        elif self.set_range.upper is None:
            sets = str(self.set_range.lower) + "+"
        else:
            sets = str(self.set_range.lower) + "-"
            sets += str(self.set_range.upper) if self.set_range.upper_inc else str(self.set_range.upper-1)
        if self.rep_range.lower is None:
            reps = "None"
        elif self.rep_range.upper is None:
            reps = str(self.rep_range.lower) + "+"
        else:
            reps = str(self.rep_range.lower) + "-"
            reps += str(self.rep_range.upper) if self.rep_range.upper_inc else str(self.rep_range.upper-1)
        if self.weight is not None:
            if self.weight.kilogram is not None:
                weight = str(self.weight.kilogram.lower) + "-" + str(self.weight.kilogram.upper)
            elif self.weight.BW:
                weight = "BW"
            else:
                weight = ""
            if self.weight.RM is not None:
                weight = str(self.weight.RM) + "RM = " + weight
            elif self.weight.percentage_range is not None:
                weight = str(self.weight.percentage_range.lower) + "-" + str(self.weight.percentage_range.upper) \
                         + "% of " + str(self.weight.RM) + " RM = " + weight
            if self.weight.band is not None:
                weight += " + " + self.weight.band
        else:
            weight = "None"
        weight = weight.strip("= ")
        weight = weight if weight != "" else "None"
        return "Sets: {sets: <8} Reps: {reps: <8} Tempo: {tempo: <8} Weight: {weight}".format(sets=sets, reps=reps, weight=weight, tempo=str(self.tempo))

    @classmethod
    def get_by_tag(cls, session, tags):
        return session.query(cls).join(cls.tags).filter(Tag.name.in_(tags)).all()

    @classmethod  # TODO check if it works when rows with type other than "exercise" are added
    def search_by_tag(cls, session, search_string):
        return session.query(Exercise). \
            join(Exercise.tags). \
            filter(and_(or_(Tag.name.match(search_string), Tag.description.match(search_string)), Tag.type == "exercise")).all()

    @classmethod
    def search_by_equipment(cls, session, search_string):
        return session.query(Exercise). \
            join(Exercise.equipment). \
            filter(or_(Equipment.name.match(search_string), Equipment.description.match(search_string))).all()

    @classmethod
    def search_by_weight(cls, session, search_string, field):
        return session.query(Exercise). \
            join(Exercise.weight). \
            filter(cast(getattr(Weight, field), String).match(search_string)).all()

    @classmethod
    def search_by_attribute(cls, session, search_string, field):
        return session.query(Exercise). \
            filter(cast(getattr(Exercise, field), String).match(search_string)).all()


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


class Equipment(Base, MixinGetByName):
    __tablename__ = 'equipment'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    exercises = relationship(
        "Exercise",
        secondary=exercise_equipment_table,
        back_populates="equipment")


class Tag(Base, MixinGetByName):
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
    training_exercise_id = Column(Integer, ForeignKey('training_exercise.id'))


class Training(Base, MixinGetByName):
    __tablename__ = 'training'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    start = Column(Time)
    end = Column(Time)
    day = relationship("Day", back_populates="training", uselist=False)
    training_exercises = relationship("TrainingExercise", cascade="save-update, merge, delete", back_populates="training")
    description = Column(Text)
    next = relationship("Training",
                        uselist=False,
                        foreign_keys='Training.next_id',
                        remote_side=[id],
                        backref=backref("prev", uselist=False))
    next_id = Column(Integer, ForeignKey('training.id'))
    is_first = Column(Boolean)
    is_template = Column(Boolean)
    training_schedule_id = Column(Integer, ForeignKey('training_schedule.id'))
    training_schedule = relationship("TrainingSchedule", back_populates="trainings")
    template_executions = relationship("Training",
                                       uselist=True,
                                       foreign_keys='Training.template_id',

                                       backref=backref("template", uselist=False, remote_side=[id]))
    template_id = Column(Integer, ForeignKey('training.id'))

    def get_exercises(self):
        exercises = []
        for exercise in self.training_exercises:
            exercises.append(exercise.get_superset())
        return exercises

    @classmethod
    def create_training_sessions(cls, s, templates):  # TREBA NAKONCI COMMITNUT PO POUZITI FUNKCIE
        training_sessions = []
        for i, template in enumerate(templates):
            training_session = Training(template=template)
            if i == 0:
                training_session.is_first = True
            else:
                training_sessions[i-1].next = training_session
            training_sessions.append(training_session)
            training_exercises = []
            s.add(training_session)
            s.flush()
            supersets = template.get_exercises()
            for superset in supersets:
                ex_ids = []
                for ex in superset:
                    ex_ids.append(ex.exercise_id)
                training_exercises.append(
                    TrainingExercise.create_superset(s, ex_ids, training_session.id))
        return training_sessions

    @classmethod
    def get_schedules_by_template(cls, session, template):
        schedules = session.query(Training).filter(and_(Training.template_id == template.id,
                                                        Training.is_first == True)).all()
        return schedules


class TrainingExercise(Base):
    __tablename__ = 'training_exercise'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    training_id = Column(Integer, ForeignKey('training.id'))
    exercise_id = Column(Integer, ForeignKey('exercise.id'))
    exercise = relationship("Exercise", back_populates="training_exercises")
    training = relationship("Training", back_populates="training_exercises")
    is_optional = Column(Boolean)
    superset_with = relationship("TrainingExercise",
                                 cascade="save-update, merge, delete",
                                 uselist=False,
                                 backref=backref("prev", uselist=False, remote_side=[id]))
    prev_training_exercise_id = Column(Integer, ForeignKey('training_exercise.id'))
    # might be wrong: https://stackoverflow.com/questions/12872873/one-to-one-self-relationship-in-sqlalchemy
    pause = Column(postgresql.INT4RANGE)
    sets = relationship("Set", cascade="save-update, merge, delete",)

    #  TODO: TEST
    @classmethod
    def create_superset(cls, session, exercise_ids, training_id):
        training = session.query(Training).filter(Training.id == training_id).first()
        training_exercises = [TrainingExercise() for _ in range(len(exercise_ids))]
        exercises = session.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
        exercises = sort_to_match(exercise_ids, exercises)
        for i, ex in enumerate(exercises):
            training_exercises[i].exercise = ex
            if ex.set_range.upper is not None:
                sets = [Set(reps=ex.rep_range.upper) for _ in range(ex.set_range.upper)]
            else:
                sets = [Set(reps=ex.rep_range.lower) for _ in range(ex.set_range.lower)]
            training_exercises[i].sets = sets
            if i == 0:
                training.training_exercises.append(training_exercises[i])
            if i != len(exercises)-1:
                training_exercises[i].superset_with = training_exercises[i+1]
        return training_exercises

    def get_superset(self):
        exercises = [self]
        ex = self
        while ex.superset_with is not None:
            exercises.append(ex.superset_with)
            ex = ex.superset_with
        return exercises


class TrainingSchedule(Base, MixinGetByName):
    __tablename__ = 'training_schedule'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phase_id = Column(Integer, ForeignKey('phase.id'))
    phase = relationship("Phase", back_populates="training_schedules")
    description = Column(Text)
    trainings = relationship("Training", back_populates="training_schedule")


class Phase(Base, MixinGetByName):
    __tablename__ = 'phase'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    training_schedules = relationship("TrainingSchedule", back_populates="phase")
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

    @classmethod
    def get_current(cls, session):
        return session.query(cls).join(cls.training_plan_history).filter(
           TrainingPlanHistory.end == None
        ).scalar()

    @classmethod  # TODO test with more t_p, phases, t_t in tables
    def get_schedules(cls, session, plan):
        return session.query(TrainingSchedule).select_from(TrainingPlan).\
            join(TrainingPlan.phases).\
            join(TrainingSchedule).\
            filter(plan.id == TrainingPlan.id).all()


class TrainingPlanHistory(Base):
    __tablename__ = 'training_plan_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    training_plan_id = Column(Integer, ForeignKey('training_plan.id'))
    training_plan = relationship("TrainingPlan", back_populates="training_plan_history")
    goals = relationship("Goal", back_populates="training_plan_history")
    start = Column(Date)
    end = Column(Date)

    @classmethod
    def get_all(cls, session):  # TODO test
        return session.query(TrainingPlanHistory)\
            .join(TrainingPlanHistory.training_plan)\
            .group_by(TrainingPlanHistory.id, TrainingPlan.name)\
            .order_by(TrainingPlanHistory.start).all()


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







