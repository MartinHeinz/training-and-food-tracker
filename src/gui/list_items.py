import decimal
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, Clock, OptionProperty, StringProperty, ListProperty, \
    DictProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.button import MDIconButton
from kivymd.dialog import MDDialog
from kivymd.list import TwoLineRightIconListItem, TwoLineIconListItem, BaseListItem, IRightBodyTouch, ILeftBodyTouch, \
    OneLineRightIconListItem, TwoLineListItem
import kivymd.material_resources as m_res
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.theming import ThemableBehavior

from gui.forms import MeasurementForm
from gui.data_visualization import MyMDCheckbox
from models.model import Ingredient
from src import dal

Builder.load_file('list_items.kv')


class LeftRightIconListItem(TwoLineRightIconListItem, TwoLineIconListItem):
    _txt_right_pad = NumericProperty(dp(40) + m_res.HORIZ_MARGINS)
    _txt_left_pad = NumericProperty(dp(72))

    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)

    _num_lines = 2

    left_icon = ObjectProperty(None)
    right_icon = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._l_icon = kwargs.pop("left_icon", "plus")
        self._r_icon = kwargs.pop("right_icon", "plus")

        self._l_icon_id = kwargs.pop("left_icon_id", "")
        self._r_icon_id = kwargs.pop("right_icon_id", "")

        self._l_icon_on_press = kwargs.pop("left_icon_on_press", None)
        self._r_icon_on_press = kwargs.pop("right_icon_on_press", None)
        super(BaseListItem, self).__init__(**kwargs)
        self.height = dp(62)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.left_icon.icon = self._l_icon
        self.left_icon.id = self._l_icon_id
        if self._l_icon_on_press is not None:
            self.left_icon.on_press = self._l_icon_on_press

        self.right_icon.icon = self._r_icon
        self.right_icon.id = self._r_icon_id
        if self._r_icon_on_press is not None:
            self.right_icon.on_press = self._r_icon_on_press


class IconLeftWidget(ILeftBodyTouch, MDIconButton):
    pass


class IconRightWidget(IRightBodyTouch, MDIconButton):
    pass


class FoodListItem(ThemableBehavior, BoxLayout):
    text = StringProperty()
    text_color = ListProperty(None)
    font_style = OptionProperty(
        'Subhead', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                            'Headline', 'Display1', 'Display2', 'Display3',
                            'Display4', 'Button', 'Icon'])
    theme_text_color = StringProperty('Primary', allownone=True)
    divider = OptionProperty('Full', options=['Full', 'Inset', None], allownone=True)

    _txt_left_pad = NumericProperty(dp(4))
    _txt_top_pad = NumericProperty()
    _txt_bot_pad = NumericProperty()
    _txt_right_pad = NumericProperty(m_res.HORIZ_MARGINS)
    _num_lines = 1
    height = NumericProperty(dp(62))

    food_fields = DictProperty()
    food_attrs = DictProperty(rebind=True)
    measurement_choose_button = ObjectProperty()
    food = ObjectProperty(Ingredient)

    def __init__(self, **kwargs):
        food = kwargs.pop("food", None)
        if food is None:
            raise Exception("Food not provided, use \"food=\" keyword argument.")
        cal = kwargs.pop("cal", "")
        amount = kwargs.pop("amount", "")
        self.menu_items = []
        super(FoodListItem, self).__init__(**kwargs)
        Clock.schedule_once(partial(self._finish_init, cal, amount, food))

    def _finish_init(self, cal, amount, food, dt=None):
        self.food_fields["cal"].text = str(cal)
        self.food_fields["amount"].text = amount
        self.food = Ingredient(food=food, amount=decimal.Decimal(amount))
        self.update_food_attrs()
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
             'text': "Grams (1g)",
             "on_press": partial(self.select_measurement, None)})

    def select_measurement(self, value):  # TODO test
        self.food.measurement = value
        self.update_fields()

    def get_measurement_text(self, m):
        return "{measurement}    ({amount} grams)" \
                    .format(measurement=m.name,
                            amount=m.grams)

    def update_food_attrs(self, *args):
        self.food_attrs = {
            "cal": self.food.get_calories(),
            "fat": round(self.food.get_attr_amount("fat"), 1),
            "protein": round(self.food.get_attr_amount("protein"), 1),
            "carbs": round(self.food.get_attr_amount("carbs"), 1)
        }

    def update_fields(self):
        for name in self.food_fields:
            if name == "cal":
                self.food_fields[name].text = str(round(self.food.get_calories()))
            elif name == "amount":
                self.food_fields[name].text = str(self.food.amount)
        if self.food.measurement is not None:
            self.measurement_choose_button.text = self.get_measurement_text(self.food.measurement)
        else:
            self.measurement_choose_button.text = "Grams (1g)"

    def on_cal_change(self, instance, value):
        amount = self.food.get_amount_by_cal(float(value))
        amount_field = self.food_fields["amount"]
        amount_field.text = str(amount)
        self.food.amount = amount
        self.update_food_attrs()

    def on_amount_change(self, instance, value):
        self.food.amount = decimal.Decimal(value)
        self.update_fields()
        self.update_food_attrs()

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
        self.food.amount = decimal.Decimal(0)
        self.update_food_attrs()
        list_view = self.parent
        list_view.remove_widget(self)


class RightCheckboxListItem(TwoLineRightIconListItem):
    height = NumericProperty(dp(62))

    training_plan = ObjectProperty(None)
    checkbox = ObjectProperty()

    def __init__(self, **kwargs):
        self.training_plan = kwargs.pop("training_plan", None)
        # if training_plan is None:
        #    raise Exception("TrainingPlan not provided, use \"training_plan=\" keyword argument.")
        super(RightCheckboxListItem, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass


class MyMDCheckboxRightWidget(IRightBodyTouch, MyMDCheckbox):
    pass


class RightIconCheckboxListItem(BaseListItem):
    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 2

    icon = StringProperty("content-save")

    _touchable_widgets = ListProperty()

    checkbox = ObjectProperty()
    icon_button = ObjectProperty()

    goal_tab_forms = ListProperty()

    def __init__(self, **kwargs):
        self.tph = kwargs.pop("tph", None)
        self.dal = kwargs.pop("data_access_layer", None)
        self.goal_tab_forms = kwargs.pop("goal_tab_forms", [])
        if self.dal is None:
            raise Exception("No Data Access Layer provided.")
        self.session = self.dal.Session()
        if self.tph is None:
            raise Exception("TrainingPlanHistory not provided, use \"tph=\" keyword argument.")
        super(BaseListItem, self).__init__(**kwargs)
        self.height = dp(72)

    def on_touch_down(self, touch):
        if self.propagate_touch_to_touchable_widgets(touch, 'down'):
            return
        super().on_touch_down(touch)

    def on_touch_move(self, touch, *args):
        if self.propagate_touch_to_touchable_widgets(touch, 'move', *args):
            return
        super().on_touch_move(touch, *args)

    def on_touch_up(self, touch):
        if self.propagate_touch_to_touchable_widgets(touch, 'up'):
            return
        super().on_touch_up(touch)

    def propagate_touch_to_touchable_widgets(self, touch, touch_event, *args):
        triggered = False
        for i in self._touchable_widgets:
            if i.collide_point(touch.x, touch.y):
                triggered = True
                if touch_event == 'down':
                    i.on_touch_down(touch)
                elif touch_event == 'move':
                    i.on_touch_move(touch, *args)
                elif touch_event == 'up':
                    i.on_touch_up(touch)
        return triggered

    def save(self):
        for tab in self.goal_tab_forms:
            tab.submit()
        self.session.commit()

    def add_goal_tab_form(self, form):
        self.goal_tab_forms.append(form)

    def remove_goal_tab_form(self, form):
        self.goal_tab_forms.remove(form)



















