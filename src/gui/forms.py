from difflib import get_close_matches

import decimal
from kivy.lang import Builder
from kivy.properties import Clock, ObjectProperty, ReferenceListProperty, ListProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.stacklayout import StackLayout
from kivy.uix.treeview import TreeViewNode, TreeView, TreeViewLabel
from kivymd.dialog import MDDialog
from kivymd.list import OneLineListItem

from gui.text_fields import MyTextField
from functools import partial

from src import dal

from models.model import Exercise, Weight, Tag, Equipment, Set, Food, Recipe, Ingredient, Measurement, FoodUsage

Builder.load_file('forms.kv')


class Form(BoxLayout):

    def __init__(self, **kwargs):
        super(Form, self).__init__(**kwargs)
        self.fields = []

        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        for field in self.get_fields():
            self.fields.append(field)

    def parse(self):
        """ Parses fields, so they can be submitted."""
        result = []
        for field in self.get_fields():
            result.append(field.get_field())
        return result

    def submit(self):
        """ Submits form to database"""
        raise NotImplementedError()

    def add_field(self, name, hint_text, helper_text="", required=False):
        """ Creates and adds new field to form. """
        field = MyTextField(hint_text=hint_text, helper_text=helper_text, required=required)
        self.add_widget(field)
        self.fields[name] = field

    def get_fields(self):
        """ Yields all children, that as form fields. """
        for child in self.children:
            if isinstance(child, MyTextField):
                yield child


class ExerciseForm(Form):

    def __init__(self, **kwargs):
        self.dal = kwargs.pop("data_access_layer", None)
        if self.dal is None:
            raise Exception("No Data Access Layer provided.")
        super(ExerciseForm, self).__init__(**kwargs)
        Clock.schedule_once(self._set_error_fun)

    def _set_error_fun(self, dt):
        name_field = next(field for field in self.get_fields() if field.name == "name")
        name_field.bind(on_text_validate=self.checks_name_input,
                        on_focus=self.checks_name_input)

    def checks_name_input(self, *args):
        name_field = next(field for field in self.get_fields() if field.name == "name")
        exercises = Exercise.get_by_name(self.dal.Session(), name_field.text)
        if exercises:
            name_field.error = True
        else:
            name_field.error = False

    def submit(self):
        session = self.dal.Session()
        exercise = Exercise()
        exercise_col_names = Exercise.__table__.columns.keys()
        weight = Weight()
        weight_col_names = Weight.__table__.columns.keys()
        exercise.weight = weight

        for field in self.parse():
            # TODO odtialto skontrolovat. Vytvorit novy session, aby sa necommitli veci z left_panel?
            if field.name in exercise_col_names:
                setattr(exercise, field.name, field.value)
            elif field.name in weight_col_names:
                setattr(weight, field.name, field.value)
            elif field.name == "tag":
                for tag in field.value:
                    # ak tag este nieje v DB pridaj novy, inak iba prirad existujuci
                    tags = Tag.get_by_name(session, tag)
                    if tags:
                        exercise.tags.append(tags[0])
                    else:
                        exercise.tags.append(Tag(name=field.name, type="exercise"))
            elif field.name == "equipment":
                for equipment in field.value:
                    # ak equipment este nieje v DB pridaj novy, inak iba prirad existujuci
                    equipments = Equipment.get_by_name(session, equipment)
                    if equipments:
                        exercise.equipment.append(equipments[0])
                    else:
                        exercise.equipment.append(Tag(name=field.name))

        session.add(exercise)
        session.commit()
        return True  # TODO close session?

    # def dismiss(self):
    #     pass


class TrainingExerciseForm(Form):
    """ Form for TrainingExercise displaying. """

    set_tree = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.exercise = kwargs.pop("exercise", None)
        self.session = kwargs.pop("session", None)
        if self.exercise is None:
            raise Exception("Exercise not provided, use \"exercise=\" keyword argument.")
        if self.session is None:
            raise Exception("Session not provided, use \"session=\" keyword argument.")
        super(TrainingExerciseForm, self).__init__(**kwargs)
        Clock.schedule_once(self._setup_set_tree)

    def _setup_set_tree(self, dt):
        # self.set_tree.clear_widgets()
        for i, set in enumerate(self.exercise.sets):
            item = TreeViewLabel(text=self.format_label(set))
            self.set_tree.add_node(item)

    def format_label(self, set):
        return "Reps: {reps: <4} Weight: {weight: <8} {PR: <10} {AMRAP: <12}" \
            .format(reps=set.reps if set.reps is not None else "",
                    weight=set.weight if set.weight is not None else "",
                    PR="Is PR" if set.is_PR is not None and set.is_PR else "",
                    AMRAP="Is AMRAP" if set.is_AMRAP is not None and set.is_AMRAP else "")

    def submit(self):
        pass


class TrainingExerciseEditForm(TrainingExerciseForm):
    """ Form for TrainingExercise editing. """

    def __init__(self, **kwargs):
        self.adding_node = None
        super(TrainingExerciseEditForm, self).__init__(**kwargs)

    def _setup_set_tree(self, dt):
        self.set_tree.clear_widgets()
        for i, set in enumerate(self.exercise.sets):
            item = TreeViewLabel(text="Set " + str(i))
            set_node = TreeViewSet(exercise=self.exercise, set_id=i, session=self.session)
            self.set_tree.add_node(item)
            self.set_tree.add_node(set_node, item)
        self.adding_node = TreeViewAddSet()
        self.set_tree.add_node(self.adding_node)

    def delete_set(self, item):  # TODO test
        """ Deletes set(item) from set_tree and updates self.exercise.sets. """
        tree = item.parent
        item_label = item.parent_node
        tree.remove_node(item)
        tree.remove_node(item_label)
        self.exercise.sets.remove(item.set)
        print("delete set")

    def add_set(self):  # TODO test
        """ Adds set(item) to set_tree and updates self.exercise.sets. """
        self.set_tree.remove_node(self.adding_node)
        i = len(self.exercise.sets)
        self.exercise.sets.append(Set())
        item = TreeViewLabel(text="Set " + str(i))
        set_node = TreeViewSet(exercise=self.exercise, set_id=i, session=self.session)
        self.set_tree.add_node(item)
        self.set_tree.add_node(set_node, item)
        self.set_tree.add_node(self.adding_node)
        print("add set")

    def submit(self):
        self.exercise.is_optional = next(field.get_field().value for field in self.children if issubclass(field.__class__, MyTextField) and field.get_field().name == "is_optional")
        self.exercise.pause = next(field.get_field().value for field in self.children if issubclass(field.__class__, MyTextField) and field.get_field().name == "pause")
        for set_field in self.set_tree.children[:-1]:
            if type(set_field) is TreeViewLabel:
                set_field.nodes[0].update_set()
            elif type(set_field) is TreeViewSet:
                set_field.update_set()
        self.session.flush()
        return True

    def dismiss(self):
        self.session.expire(self.exercise)
        return True


class TreeViewSet(BoxLayout, TreeViewLabel):
    def __init__(self, **kwargs):
        self.exercise = kwargs.pop("exercise", None)
        self.set_id = kwargs.pop("set_id", None)
        self.session = kwargs.pop("session", None)
        if self.exercise is None:
            raise Exception("Exercise not provided, use \"exercise=\" keyword argument.")
        if self.set_id is None:
            raise Exception("Set id not provided, use \"set_id=\" keyword argument.")
        if self.session is None:
            raise Exception("Session not provided, use \"session=\" keyword argument.")
        self.set = self.exercise.sets[self.set_id]
        super(TreeViewSet, self).__init__(**kwargs)
        self.fields = {f.get_field().name: f for f in self.children if issubclass(f.__class__, MyTextField)}
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.update_set()
        self.update_text()
        for field in self.children:
            if issubclass(field.__class__, MyTextField):
                field.bind(text=self.update_text)

    def update_text(self, *args):
        self.parent_node.text = "Reps: {reps: <4} Weight: {weight: <8} {PR: <10} {AMRAP: <12}" \
            .format(reps=self.fields["reps"].get_field().value,
                    weight=self.fields["weight"].get_field().value,
                    PR="Is PR" if self.fields["is_PR"].get_field().value else "",
                    AMRAP="Is AMRAP" if self.fields["is_AMRAP"].get_field().value else "")

    def update_set(self):
        """ Updates set in session based on set fields. """
        for field in self.children:
            if issubclass(field.__class__, MyTextField):
                val = field.get_field().value
                setattr(self.set, field.get_field().name, val if val != "" else None)


class TreeViewAddSet(BoxLayout, TreeViewLabel):
    pass


class TreeViewFood(BoxLayout, TreeViewLabel):  # TODO

    food_fields = ListProperty()
    measurement_choose_button = ObjectProperty()

    def __init__(self, **kwargs):
        self.food = kwargs.pop("food", None)
        if self.food is None:
            raise Exception("FoodUsage or Ingredient not provided, use \"food=\" keyword argument.")
        self.dropdown_values = [] if not self.food.food.measurements else \
            [getattr(m, "name") for m in self.food.food.measurements]
        self.menu_items = []
        super(TreeViewFood, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.update_fields()
        self.update_text()
        self.parent_node.font_name = "RobotoMono-Regular"
        self.parent_node.font_size = 14
        for field in self.children:
            if issubclass(field.__class__, MyTextField):
                field.bind(text=self.update_text)
        self.create_measurement_items()

    def create_measurement_items(self, clear=False):
        if clear:
            self.menu_items = []
        if self.food.food.measurements is not None:
            for m in self.food.food.measurements:
                text = self.get_measurement_text(m)
                self.menu_items.append(
                    {'viewclass': 'MDMenuItem',
                     'text': text,
                     "on_press": partial(self.select_measurement, m)})
        self.menu_items.append(
            {'viewclass': 'MDMenuItem',
             'text': "1 gram",
             "on_press": partial(self.select_measurement, None)})

    def select_measurement(self, value):  # TODO test
        self.food.measurement = value
        self.update_fields()
        self.update_text()

    def get_measurement_text(self, m):
        return "{measurement}    ({amount} grams)" \
                    .format(measurement=m.name,
                            amount=m.grams)

    def update_text(self, update_day_fields=False, *args):
        self.parent_node.text = self.food.food.name.ljust(30) + "Cal: {cal: <8} {amount: <16} Fat: {fat: <8} Protein: {protein: <8} Carbs: {carbs: <8}" \
            .format(cal=str(self.food.get_calories()),
                    amount=str(self.food.amount) + " " + getattr(self.food.measurement, "name", "grams"),
                    fat=round(self.food.get_attr_amount("fat"), 1),
                    protein=round(self.food.get_attr_amount("protein"), 1),
                    carbs=round(self.food.get_attr_amount("carbs"), 1))
        if update_day_fields:
            self.parent_node.parent_node.update_text(True)

    def update_fields(self):
        for f in self.food_fields:
            name = f.get_field().name
            if name == "cal":
                f.text = str(round(self.food.get_calories()))
            elif name == "amount":
                f.text = str(self.food.amount)
        if self.food.measurement is not None:
            self.measurement_choose_button.text = self.get_measurement_text(self.food.measurement)
        else:
            self.measurement_choose_button.text = "1 gram"

    def on_cal_change(self, instance, value):
        amount = self.food.get_amount_by_cal(float(value))
        amount_field = next(f for f in self.food_fields if f.get_field().name == "amount")
        amount_field.text = str(amount)
        self.food.amount = amount
        self.update_text(True)

    def on_amount_change(self, instance, value):
        self.food.amount = decimal.Decimal(value)
        self.update_fields()
        self.update_text(True)

    def add_measurement(self):
        content = MeasurementForm(dal=dal, food=self.food.food)
        dialog = MDDialog(title="Add Measurement",
                          content=content,
                          size_hint=(.3, .4),
                          pos_hint={"x": 0.6},
                          auto_dismiss=False)

        def submit():
            if content.submit():
                self.create_measurement_items(True)
                dialog.dismiss()
                print("submitted")

        dialog.add_action_button("Submit",
                                 action=lambda *x: submit())
        dialog.add_action_button("Dismiss",
                                 action=lambda *x: dialog.dismiss())
        dialog.open()

    def delete_food(self):  # TODO test
        """ Deletes food(item) from meal_tree and removes self.food from meal/recipe. """
        try:
            meal = self.food.meal
            meal.foods.remove(self.food)
            self.parent_node.parent_node.update_text(True)
            print("delete food")
        except AttributeError:
            recipe = self.food.recipe
            recipe.ingredients.remove(self.food)
            self.parent_node.parent_node.update_text(True)
            print("delete ingredient")
        tree = self.parent
        item_label = self.parent_node
        tree.remove_node(self)
        tree.remove_node(item_label)


class TreeViewRecipe(BoxLayout, TreeViewNode):  # TODO

    recipe_label = ObjectProperty()

    def __init__(self, **kwargs):
        self.recipe = kwargs.pop("recipe", None)
        if self.recipe is None:
            raise Exception("Recipe not provided, use \"recipe=\" keyword argument.")
        self.meal_tree_box = kwargs.pop("meal_tree_box", None)
        if self.meal_tree_box is None:
            raise Exception("MealTreeBox not provided, use \"meal_tree_box=\" keyword argument.")
        self.meal_tree = self.meal_tree_box.meal_tree
        self.parent_node = kwargs.pop("parent_node", None)
        if self.parent_node is None:
            raise Exception("Parent Node not provided, use \"parent_node=\" keyword argument.")
        super(TreeViewRecipe, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        # self.update_meal_recipe()
        self.update_text()
        self.font_name = "RobotoMono-Regular"
        self.meal_node = self.meal_tree.add_node(self, self.parent_node)
        for ing in self.recipe.ingredients:
            self.add_food_node(ing)
        self.recipe_label.on_touch_down = self.insert_copied

    def add_food_node(self, ingredient):
        food_node = TreeViewLabel(text=ingredient.food.name)
        n2 = self.meal_tree.add_node(food_node, self.meal_node)
        food_node_fields_box = TreeViewFood(food=ingredient)
        self.meal_tree.add_node(food_node_fields_box, n2)

    def insert_copied(self, *args):
        """ Insert copied food from copied_exercise, if it is not None and update self.recipe. """
        copy = self.get_copied_food()
        if copy is not None and type(copy.food) == Food:
            fsp = self.get_food_search_panel()
            fsp.reset_food_icon()

            ingredient = Ingredient(food=copy.food, amount=decimal.Decimal(100))
            if self.recipe.ingredients is None:
                self.recipe.ingredients = [ingredient]
            else:
                self.recipe.ingredients.append(ingredient)

            self.add_food_node(ingredient)

            fsp.remove_copy()
            self.update_text(True)
        else:
            print("empty or not a food")

    def get_copied_food(self):
        return self.meal_tree_box.screen.right_panel.get_copied_food()

    def get_food_search_panel(self):
        return self.meal_tree_box.screen.right_panel.food_search_panel

    def update_text(self, update_day_fields=False, *args):
        cal_sum = sum(f.get_calories() for f in self.recipe.ingredients)
        self.recipe_label.text = self.recipe.name.ljust(30) + "Cal: {cal: <8} Fat: {fat: <8} Protein: {protein: <8} Carbs: {carbs: <8}" \
                       .format(cal=str(round(cal_sum, 1)),
                               fat=str(round(self.recipe.get_attr_amount("fat"), 1)),
                               protein=str(round(self.recipe.get_attr_amount("protein"), 1)),
                               carbs=str(round(self.recipe.get_attr_amount("carbs"), 1)))
        if update_day_fields:
            self.parent_node.update_text(True)

    def delete_recipe(self):  # TODO test
        """ Deletes meal(item) from meal_tree and removes self.recipe from meal. """
        meal = self.recipe.meal
        meal.recipes.remove(self.recipe)
        self.parent_node.update_text(True)

        tree = self.parent
        # item_label = self.parent_node
        tree.remove_node(self)
        # tree.remove_node(item_label)
        print("delete recipe")


class TreeViewMeal(BoxLayout, TreeViewNode):  # TODO

    meal_label = ObjectProperty()

    def __init__(self, **kwargs):
        self.meal = kwargs.pop("meal", None)
        self.meal_tree_box = kwargs.pop("meal_tree_box", None)
        if self.meal is None:
            raise Exception("Meal not provided, use \"meal=\" keyword argument.")
        if self.meal_tree_box is None:
            raise Exception("mealTreeBox box not provided, use \"meal_tree_box=\" keyword argument.")
        self.meal_tree = self.meal_tree_box.meal_tree
        super(TreeViewMeal, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        # self.update_food()
        self.update_text()
        for food_usage in self.meal.foods:
            self.add_food_node(food_usage)
        for recipe_exec in self.meal.recipes:
            recipe_node = TreeViewRecipe(recipe=recipe_exec,
                                         meal_tree_box=self.meal_tree_box,
                                         parent_node=self)
        self.meal_label.on_touch_down = self.insert_copied

    def add_food_node(self, food_usage):
        food_node = TreeViewLabel(text=food_usage.food.name)
        n1 = self.meal_tree.add_node(food_node, self)
        food_node_fields_box = TreeViewFood(food=food_usage)
        self.meal_tree.add_node(food_node_fields_box, n1)

    def insert_copied(self, *args):
        """ Insert copied food from copied_exercise, if it is not None and update self.meal. """
        copy = self.get_copied_food()
        if copy is not None:
            fsp = self.get_food_search_panel()
            fsp.reset_food_icon()
            if type(copy.food) == Food:
                food = FoodUsage(food=copy.food, amount=decimal.Decimal(100))
                if self.meal.foods is None:
                    self.meal.foods = [food]
                else:
                    self.meal.foods.append(food)

                self.add_food_node(food)
            else:  # copy.food is Recipe
                recipe_exec = Recipe(name=copy.food.name, is_template=False, notes="",
                                     serving_size=decimal.Decimal(1), template=copy.food)
                for ing in copy.food.ingredients:
                    recipe_exec.add_food(ing.food, ing.amount)
                self.meal.add_recipe(recipe_exec)
                recipe_node = TreeViewRecipe(recipe=recipe_exec,
                                             meal_tree_box=self.meal_tree_box,
                                             parent_node=self)
            fsp.remove_copy()
            self.update_text(True)

    def get_copied_food(self):
        return self.meal_tree_box.screen.right_panel.get_copied_food()

    def get_food_search_panel(self):
        return self.meal_tree_box.screen.right_panel.food_search_panel

    def update_text(self, update_day_fields=False, *args):
        self.meal_label.text = self.meal.name.ljust(30) + "Cal: {cal: <8} Fat: {fat: <8} Protein: {protein: <8} Carbs: {carbs: <8}" \
            .format(cal=str(round(self.meal.get_calories(), 1)),
                    fat=str(round(self.meal.get_attr_amount("fat"), 1)),
                    protein=str(round(self.meal.get_attr_amount("protein"), 1)),
                    carbs=str(round(self.meal.get_attr_amount("carbs"), 1)))
        if update_day_fields:
            self.meal_tree_box.screen.right_panel.update_calculated_day_fields()

    def delete_meal(self):  # TODO test
        """ Deletes meal(item) from meal_tree and removes self.food from meal/recipe. """
        day = self.meal.day
        day.meals.remove(self.meal)
        self.meal_tree_box.screen.right_panel.update_calculated_day_fields()

        self.meal_tree.remove_node(self)
        # tree.remove_node(item_label)
        print("delete meal")


class FoodForm(Form):

    def __init__(self, **kwargs):
        self.dal = kwargs.pop("data_access_layer", None)
        if self.dal is None:
            raise Exception("No Data Access Layer provided.")
        super(FoodForm, self).__init__(**kwargs)
        Clock.schedule_once(self._set_error_fun)

    def _set_error_fun(self, dt):
        name_field = next(field for field in self.get_fields() if field.name == "name")
        name_field.bind(on_text_validate=self.checks_name_input,
                        on_focus=self.checks_name_input)

    def checks_name_input(self, *args):
        name_field = next(field for field in self.get_fields() if field.name == "name")
        foods = Food.get_by_name(self.dal.Session(), name_field.text)
        if foods:
            name_field.error = True
        else:
            name_field.error = False

    def submit(self):
        session = self.dal.Session()
        food = Food()
        exercise_col_names = Food.__table__.columns.keys()

        for field in self.parse():
            if field.name in exercise_col_names:
                setattr(food, field.name, field.value)

        session.add(food)
        session.commit()
        return True


class MeasurementForm(Form):

    def __init__(self, **kwargs):
        self.food = kwargs.pop("food", None)
        self.dal = kwargs.pop("dal", None)
        if self.food is None:
            raise Exception("Food not provided, use \"food=\" keyword argument.")
        if self.dal is None:
            raise Exception("Data Access Layer not provided, use \"dal=\" keyword argument.")
        super(MeasurementForm, self).__init__(**kwargs)

    def submit(self):
        measurement = Measurement()
        for f in self.get_fields():
            if f.get_field().type == "float":
                setattr(measurement, f.get_field().name, decimal.Decimal(f.get_field().value))
            else:
                setattr(measurement, f.get_field().name, f.get_field().value)
        if self.food.measurements is None:
            self.food.measurements = [measurement]
        else:
            self.food.measurements.append(measurement)
        return True


