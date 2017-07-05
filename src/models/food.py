from sqlalchemy import Table, Column, Integer, ForeignKey, Date, Numeric, String, Text, Boolean, Interval, Time
from sqlalchemy.orm import relationship, backref
from src.models.base import Base
from sqlalchemy.dialects import postgresql
# from src import engine


recipe_tag_table = Table('recipe_tag', Base.metadata,
                         Column("recipe_id", Integer, ForeignKey('recipe.id')),
                         Column('tag_id', Integer, ForeignKey('tag.id')),
                         extend_existing=True
                         )


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
    amount = Column(Numeric(precision=3, scale=2))
    meal = relationship("Meal", back_populates="recipes")
    recipe = relationship("Recipe", back_populates="meals")


class MealFood(Base):
    __tablename__ = 'meal_food'
    __table_args__ = {'extend_existing': True}
    meal_id = Column(Integer, ForeignKey('meal.id'), primary_key=True)
    food_id = Column(Integer, ForeignKey('food.id'), primary_key=True)
    amount = Column(Integer)
    meal = relationship("Child", back_populates="foods")
    food = relationship("Parent", back_populates="meals")


class Food(Base):
    __tablename__ = 'food'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cal = Column(Integer)
    protein = Column(Integer)
    carbs = Column(Integer)
    fat = Column(Integer)
    fibre = Column(Integer)
    measurements = relationship("FoodMeasurement", back_populates="food")
    meals = relationship("MealFood", back_populates="food")
    recipes = relationship("FoodRecipe", back_populates="food")


class Measurement(Base):
    __tablename__ = 'measurement'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    foods = relationship("FoodMeasurement", back_populates="measurement")


class Meal(Base):
    __tablename__ = 'meal'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    foods = relationship("FoodMeasurement", back_populates="meal")
    recipes = relationship("MealRecipe", back_populates="meal")
    day_id = Column(Integer, ForeignKey('day.id'))
    day = relationship("Day", back_populates="meals")


class Recipe(Base):
    __tablename__ = 'recipe'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    serving_size = Column(Numeric(precision=3, scale=2))
    notes = Column(Text)
    foods = relationship("FoodRecipe", back_populates="recipe")
    meals = relationship("MealRecipe", back_populates="recipe")
    tags = relationship(
        "Tag",
        secondary=recipe_tag_table,
        back_populates="recipes")
