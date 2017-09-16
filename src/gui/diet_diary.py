import datetime
from collections import namedtuple
from difflib import get_close_matches
from itertools import chain

import decimal

from kivy.core.window import Window
from kivy.properties import ObjectProperty, Clock, NumericProperty, partial, ReferenceListProperty, ListProperty, \
    DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.treeview import TreeViewNode, TreeViewLabel
from kivymd.dialog import MDDialog
from kivymd.list import OneLineListItem
from psycopg2._range import NumericRange

from gui.forms import TreeViewFood, TreeViewRecipe, TreeViewMeal, FoodForm
from gui.list_items import LeftRightIconListItem, FoodListItem
from gui.text_fields import MyTextField
from models.model import Day, Meal, Food, Recipe, Ingredient

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt

from src import dal

session = None


class DietDiary(Screen):
    left_panel = ObjectProperty()
    right_panel = ObjectProperty()

    def __init__(self, **kwargs):
        super(DietDiary, self).__init__(**kwargs)
        global session
        if session is None:
            session = dal.Session()

    def on_pre_enter(self, *args):
        if not self.left_panel.meal_tree_box.meal_tree.root.nodes:
            self.left_panel.meal_tree_box.setup_food_tree()

    def on_pre_leave(self, *args):
        session.commit()  # TODO close session?


class LeftPanel(StackLayout):
    add_meal_box = ObjectProperty()
    meal_tree_box = ObjectProperty()
    screen = ObjectProperty()
    day = ObjectProperty(Day())

    def __init__(self, **kwargs):
        super(LeftPanel, self).__init__(**kwargs)
        # self.day = Day.get_by_date(session, datetime.date.today())
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.bind(day=self.refresh_meal_tree)
        self.day = self.get_right_panel().get_day()
        self.refresh_meal_tree()

    def add_node(self, meal):
        self.meal_tree_box.add_node(meal)

    def refresh_meal_tree(self, instance=None, value=None):
        self.meal_tree_box.clear_nodes()
        self.meal_tree_box.setup_food_tree()

    def get_right_panel(self):
        return self.screen.right_panel

    def update_day(self, instance=None, value=None, day=None):
        self.day = day


class RightPanel(BoxLayout):
    day_panel = ObjectProperty()
    food_search_panel = ObjectProperty()
    screen = ObjectProperty()

    def __init__(self, **kwargs):
        super(RightPanel, self).__init__(**kwargs)

    def get_left_panel(self):
        return self.screen.left_panel

    def get_day(self):
        return self.day_panel.day

    def get_copied_food(self):
        return self.food_search_panel.copied_food

    def update_calculated_day_fields(self):
        self.day_panel.update_calculated_fields()


class DayPanel(StackLayout):
    date_field = ObjectProperty()
    search_button = ObjectProperty()
    chart = ObjectProperty()
    day = ObjectProperty(Day())
    fields = ListProperty()
    target_fields = ListProperty()

    def __init__(self, **kwargs):
        super(DayPanel, self).__init__(**kwargs)
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor((0.1875, 0.1875, 0.1875))
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.chart.add_widget(FigureCanvasKivyAgg(figure=self.fig))  # plt.gcf()
        lp = self.parent.get_left_panel()
        self.bind(day=partial(lp.update_day, self.day))
        self.day = Day.get_by_date(session, datetime.date.today())
        self.update_fields()
        self.update_chart()
        self.update_target_fields()
        self.set_date_field(self.day.date)

    def set_date_field(self, date):
        self.date_field.text = date.strftime("%d.%m.%Y")

    def change_day(self):  # TODO ak new_day je None, vytvorit novy den a add-nut ho do session
        new_day = Day.get_by_date(session, self.date_field.get_field().value)
        if new_day is not None and new_day != self.day:
            self.day = new_day
            self.update_fields()
            self.update_chart()
            self.update_target_fields()
            self.set_date_field(self.day.date)

    def update_calculated_fields(self):
        self.update_fields()
        self.update_chart()

    def update_fields(self):
        """ Updates Cals, Fats... fields based on current day. """
        for f in self.fields:
            if f.name == "cal":
                f.text = str(round(sum(m.get_calories() for m in self.day.meals), 1))
            else:
                f.text = str(round(sum(m.get_attr_amount(f.name) for m in self.day.meals), 1))

    def update_chart(self):
        """ Updates Chart based on field values. """
        self.ax.patches = []
        self.ax.texts = []
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = 'Fats', 'Protein', 'Carbs'
        amounts_sum = sum(v for k, v in self.get_fields_values().items() if k not in ["fat", "protein", "carbs"])  # sum of amounts of f, p, c
        cal_sum = sum(m.get_calories() for m in self.day.meals)
        if cal_sum != 0:
            amounts = [(v/amounts_sum)*100 for k, v in self.get_fields_values().items() if k not in ["fat", "protein", "carbs"]]  # amounts of f, p, c
            sizes = [(v*(9 if k == "fat" else 4)/cal_sum)*100
                     for k, v in self.get_fields_values().items() if k in ["fat", "protein", "carbs"]]
        else:
            sizes = [33, 33, 33]
        explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        _, texts, autotexts = self.ax.pie(sizes, explode=explode, radius=1, labels=labels, autopct='%1.1f%%',
                                          shadow=True, startangle=90, colors=["C1", "C2", "C3"])

        for t in chain(autotexts, texts):
            t.set_color('white')
        self.ax.set_aspect("equal")
        # ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle. -> fucks up size of pie
        self.fig.canvas.draw_idle()

    def update_target_fields(self):  # TODO test
        """ Updates fields with cal, fat... targets. """
        for f in self.target_fields:
            val = getattr(self.day, f.get_field().name)
            val = NumericRange(0, 1) if val is None else val
            new_val = str(val.lower) + "-" + str(val.upper)
            if new_val == f.text:  # to force update_targets
                f.text = ""
            f.text = new_val

    def update_targets(self, instance, value):  # TODO test
        """ Updates selected days targets fields value. """
        name = instance.get_field().name
        field_val = instance.get_field().value
        new_val = NumericRange(0, 1) if field_val in ["", None, "None"] else field_val
        setattr(self.day, name, new_val)

    def get_fields_values(self):
        res = {}
        for f in self.fields:
            if f.name == "cal":
                res[f.name] = round(sum(m.get_calories() for m in self.day.meals), 1)
            else:
                res[f.name] = round(sum(m.get_attr_amount(f.name) for m in self.day.meals), 1)
        return res


class FoodSearchPanel(BoxLayout):
    list_height = NumericProperty(100)
    search_layout = ObjectProperty()

    def __init__(self, **kwargs):
        self.copied_food = None
        super(FoodSearchPanel, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.search_layout.search_field.search = self.search

    def search(self):
        """ Searches DB for food based on values in search_layout fields. """
        available_search_values = ["food", "recipe", "cal", "protein", "carbs", "fat", "fibre", "brand", "food tag", "recipe tag"]
        search_input = self.search_layout.get_search_field_value()
        search_by_field_value = self.search_layout.get_search_by_value()
        result_list = self.search_layout.get_result_list()
        result_list.clear_widgets()
        search_by_value = ""
        if search_by_field_value:
            search_result_list = get_close_matches(search_by_field_value, available_search_values)
            if search_result_list:
                search_by_value = search_result_list[0]
        if search_by_value == "recipe":
            item_create = OneLineListItem(text="Create New Recipe",
                                          on_press=self.show_create_recipe_screen
                                          )
        else:
            item_create = OneLineListItem(text="Create New Food",
                                          on_press=self.show_create_food_dialog)
        result_list.add_widget(item_create)
        if search_by_value in available_search_values:
            self.search_layout.set_search_by_value(search_by_value)
            if search_by_value == "food":
                rows = Food.search_by_attribute(session, search_input, "name")
            elif search_by_value == "food tag":
                rows = Food.search_by_tag(session, search_input)
            elif search_by_value == "recipe tag":
                rows = Recipe.search_by_tag(session, search_input)
            elif search_by_value == "recipe":
                rows = Recipe.search_by_attribute(session, search_input, "name", only_template=True)
            elif search_by_value in ["cal", "protein", "carbs", "fat", "fibre"] and search_input.replace('.', '', 1).isdigit():
                rows = Food.get_closest_matches(session, float(search_input), search_by_value, 10)
            else:
                rows = Food.search_by_attribute(session, search_input, search_by_value)
            for row in rows:
                item = LeftRightIconListItem(text=row.name,
                                             secondary_text=row.get_field_secondary_text(),
                                             left_icon="content-copy",
                                             left_icon_id="li_icon_" + str(row.id),
                                             right_icon="magnify",
                                             right_icon_id="li_icon_r_" + str(row.id),
                                             #right_icon_on_press=partial(self.highlight_tabs, row)
                                             )
                item.left_icon.on_press = partial(self.copy_food, item, row)
                result_list.add_widget(item)

    def show_create_food_dialog(self, *args):
        """ Shows dialog for creation of new food."""
        content = FoodForm(data_access_layer=dal)
        dialog = MDDialog(title="Create Food",
                          content=content,
                          size_hint=(.3, .8),
                          pos_hint={"x": 0.1},
                          auto_dismiss=False)

        def submit():
            if content.submit():
                dialog.dismiss()
                print("submitted")

        dialog.add_action_button("Submit",
                                 action=lambda *x: submit())
        dialog.add_action_button("Dismiss",
                                 action=lambda *x: dialog.dismiss())
        dialog.open()

    def show_create_recipe_screen(self, *args):
        """ Shows screen for creation of new recipe template. """
        diet_diary = self.parent.screen
        manager = diet_diary.manager
        new_screen = next(screen for screen in manager.screens if isinstance(screen, AddRecipeScreen))
        manager.current = new_screen.name
        new_screen.return_to_screen = diet_diary

    def copy_food(self, li, food):
        """ Used to copy food from search list. """
        if self.copied_food is not None:
            self.copied_food.list_item.left_icon.icon = "content-copy"
        li.left_icon.icon = "content-duplicate"
        CopiedFood = namedtuple("CopiedFood", ["list_item", "food"])
        self.copied_food = CopiedFood(li, food)

    def reset_food_icon(self):
        self.copied_food.list_item.left_icon.icon = "content-copy"

    def remove_copy(self):
        self.copied_food = None


class AddMealBox(BoxLayout):
    name_field = ObjectProperty()
    time_field = ObjectProperty()
    submit_button = ObjectProperty()

    def __init__(self, **kwargs):
        super(AddMealBox, self).__init__(**kwargs)

    def add_meal(self):
        name = self.name_field.get_field().value
        time = self.time_field.get_field().value
        meals = self.parent.day.meals
        if meals is not None:
            meals.append(Meal(name=name, time=time))
        else:
            meals = [Meal(name=name, time=time)]
        self.parent.add_node(meals[-1])


class MealTreeBox(BoxLayout):
    meal_tree = ObjectProperty()
    screen = ObjectProperty()

    def __init__(self, **kwargs):
        super(MealTreeBox, self).__init__(**kwargs)
        Clock.schedule_once(self.setup_food_tree)

    def setup_food_tree(self, dt=None):
        meals = sorted(self.get_meals(), key=lambda m: datetime.time(0, 0, 0) if getattr(m, "time") is None else getattr(m, "time"))
        for meal in meals:
            self.meal_tree.add_node(TreeViewMeal(meal=meal, meal_tree_box=self))

    def clear_nodes(self):
        for node in self.meal_tree.root.nodes[:]:
            self.meal_tree.remove_node(node)

    def add_node(self, meal):
        """Add new meal as node to tree at position based on time"""
        node = TreeViewMeal(meal=meal, meal_tree_box=self)
        nodes = self.meal_tree.root.nodes
        sorted_nodes = sorted(chain(nodes, [node]), key=lambda n: datetime.time(0, 0, 0) if getattr(n.meal, "time") is None else getattr(n.meal, "time"))
        self.clear_nodes()
        for n in sorted_nodes:
            self.meal_tree.add_node(n)

    def get_meals(self):
        day = self.parent.day if self.parent.day is not None else Day.get_by_date(session, datetime.date.today())
        return day.meals


class AddRecipeScreen(Screen):

    ingredients_list = ObjectProperty()
    search_layout = ObjectProperty()
    sum_labels = DictProperty()
    return_to_screen = ObjectProperty(None, allownone=True)
    toolbar = ObjectProperty(None)
    recipe_attrs = DictProperty()

    def __init__(self, **kwargs):
        self.session = dal.Session()
        super(AddRecipeScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._set_error_fun)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.search_layout.search_field.search = self.search

    def on_enter(self, *args):
        contains = next((True for ar in self.toolbar.right_action_items if ar[0] == "content-save"), False)
        if contains:
            print("contains")
        else:
            self.toolbar.right_action_items.append(["content-save", lambda x: self.save_recipe()])
            print("doesnt contain")

    def on_leave(self, *args):
        self.remove_save_button()
        self.return_to_screen = None

    def remove_save_button(self):
        self.toolbar.right_action_items[:] = [item for item in self.toolbar.right_action_items if
                                              item[0] != "content-save"]

    def save_recipe(self):
        self._save()
        if self.return_to_screen is not None:
            self.manager.current = self.return_to_screen.name
        else:
            self.reset_screen()

    def _save(self):
        recipe = Recipe(ingredients=[], is_template=True)
        for attr in self.recipe_attrs:
            if attr == "serving_size":
                setattr(recipe, attr, decimal.Decimal(self.recipe_attrs[attr].get_field().value))
            else:
                setattr(recipe, attr, self.recipe_attrs[attr].get_field().value)
        for food_field in self.ingredients_list.children:
            recipe.ingredients.append(food_field.food)
        self.session.add(recipe)
        self.session.commit()
        self.session.close()
        print("save recipe")

    def reset_screen(self):
        for attr in self.recipe_attrs:
            self.recipe_attrs[attr].text = ""
        self.ingredients_list.clear_widgets()
        self.search_layout.set_search_by_value("")
        self.search_layout.set_search_field_value("")
        result_list = self.search_layout.get_result_list()
        result_list.clear_widgets()

        print("reset screen fields, list and search")

    def _set_error_fun(self, dt):
        self.recipe_attrs["name"].bind(on_text_validate=self.checks_name_input,
                                       on_focus=self.checks_name_input)

    def checks_name_input(self, *args):
        name_field = self.recipe_attrs["name"]
        recipes = Recipe.get_by_name(self.session, name_field.text)
        if recipes:
            name_field.error = True
        else:
            name_field.error = False

    def search(self):
        """ Searches DB for food based on values in search_layout fields. """
        available_search_values = ["food", "name", "cal", "protein", "carbs", "fat", "fibre", "brand"]
        search_input = self.search_layout.get_search_field_value()
        search_by_field_value = self.search_layout.get_search_by_value()
        result_list = self.search_layout.get_result_list()
        result_list.clear_widgets()
        search_by_value = ""
        if search_by_field_value:
            search_result_list = get_close_matches(search_by_field_value, available_search_values)
            if search_result_list:
                search_by_value = search_result_list[0]
        if search_by_value in available_search_values:
            self.search_layout.set_search_by_value(search_by_value)
            if search_by_value in ["food", "name"]:
                rows = Food.search_by_attribute(self.session, search_input, "name")
            elif search_by_value in ["cal", "protein", "carbs", "fat", "fibre"] and search_input.replace('.', '', 1).isdigit():
                rows = Food.get_closest_matches(self.session, float(search_input), search_by_value, 10)
            else:
                rows = Food.search_by_attribute(self.session, search_input, search_by_value)
            for row in rows:
                item = LeftRightIconListItem(text=row.name,
                                             secondary_text=row.get_field_secondary_text(),
                                             left_icon="plus",
                                             left_icon_id="li_icon_" + str(row.id),
                                             right_icon="magnify",
                                             right_icon_id="li_icon_r_" + str(row.id),
                                             # right_icon_on_press=partial(self.highlight_tabs, row)
                                             )
                item.left_icon.on_press = partial(self.copy_food, item, row)  # TODO
                result_list.add_widget(item)

    def copy_food(self, item, food):
        li = FoodListItem(food=food, text=food.name, cal=food.cal, amount="100")
        li.bind(food_attrs=self.update_sum_labels)
        self.ingredients_list.add_widget(li)
        print("copy recipe")

    def update_sum_labels(self, instance, value):
        label_values = {"cal": 0, "protein": 0, "fat": 0, "carbs": 0}
        for li in self.ingredients_list.children:
            for name in li.food_attrs:
                label_values[name] += li.food_attrs[name]
        for name in self.sum_labels:
            widget = self.sum_labels[name]
            widget.text = "{name} {value}".format(name=self.sum_labels[name].text.split()[0],
                                                                 value=str(label_values[name]))
        size = Window.size
        Window.size = (size[0] + 0.001, size[1])  # needed to retain sum_labels size
        print("update_sum_labels")




















