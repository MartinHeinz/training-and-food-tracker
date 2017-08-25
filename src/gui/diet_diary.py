from datetime import date

from kivy.properties import ObjectProperty, Clock, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.treeview import TreeViewNode

from gui.text_fields import MyTextField
from models.model import Day

from src import dal

session = None


class DietDiary(Screen):

    def __init__(self, **kwargs):
        super(DietDiary, self).__init__(**kwargs)
        global session
        if session is None:
            session = dal.Session()

    def on_leave(self, *args):
        session.commit()  # TODO close session?


class LeftPanel(StackLayout):
    add_meal_box = ObjectProperty()

    def __init__(self, **kwargs):
        super(LeftPanel, self).__init__(**kwargs)
        self.day = Day.get_by_date(session, date.today())


class RightPanel(BoxLayout):
    day_panel = ObjectProperty()
    food_search_panel = ObjectProperty()

    def __init__(self, **kwargs):
        super(RightPanel, self).__init__(**kwargs)


class DayPanel(StackLayout):
    date_field = ObjectProperty()
    # others_tree = ObjectProperty()

    def __init__(self, **kwargs):
        super(DayPanel, self).__init__(**kwargs)
    #     Clock.schedule_once(self._setup_set_tree)
    #
    # def _setup_set_tree(self, dt):
    #     self.others_tree.clear_widgets()
    #     values = ["Fiber", "Sodium"]
    #     node = OtherValuesTreeBox(orientation="horizontal", spacing=10, padding=(5, 0, 5, 0),
    #                               size_hint_y=None, height=60)
    #     for i, val in enumerate(values):
    #         field = MyTextField(name=val.lower(), type="float", input_filter="float", hint_text=val, helper_text="Target " + val + ".",
    #                             size_hint_x=1.0/len(values), )
    #         node.add_widget(field)
    #     self.others_tree.add_node(node)
    #     self.others_tree.toggle_node(self.others_tree.root)
    #     self.others_tree.root.no_selection = True


class FoodSearchPanel(BoxLayout):
    list_height = NumericProperty(100)


class AddMealBox(BoxLayout):
    name_field = ObjectProperty()
    time_field = ObjectProperty()


class MealTreeBox(BoxLayout):
    meal_tree = ObjectProperty()

    def __init__(self, **kwargs):
        super(MealTreeBox, self).__init__(**kwargs)
        Clock.schedule_once(self._setup_set_tree)

    def _setup_set_tree(self, dt):
        self.meal_tree.clear_widgets()
        meals = self.get_meals()
        for meal in meals:
            pass  # TODO pridat node-y s meal + food

    def get_meals(self):
        day = self.parent.day
        return day.meals


class OtherValuesTreeBox(BoxLayout, TreeViewNode):
    pass
