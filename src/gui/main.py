from datetime import date, timedelta
from traceback import format_exc
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.accordion import MDAccordionSubItem, MDAccordionItem
from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivymd.list import TwoLineListItem
from kivymd.textfields import MDTextField
from models.util import get_model_by_tablename, get_model
from sqlalchemy.sql import text
from sqlalchemy.exc import DataError
from kivymd.theming import ThemeManager

from kivy.app import App
from kivy.properties import ObjectProperty, Clock
from src import dal, session
from functools import partial
from kivy.config import Config

from gui.training_screen import *
from gui.diet_diary import *
from gui.data_visualization import *
from gui.goals import *
from gui.body_composition import *


class MainLayout(FloatLayout):
    nav_drawer = ObjectProperty(None, allownone=True)
    table_modification_accordion = ObjectProperty(None, allownone=True)
    sm = ObjectProperty(None)
    # table_form = ObjectProperty(None, allownone=True)
    # search_box = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        Clock.schedule_once(self.create_subitems)

    def create_subitems(self, dt):
        pass


class TableModifications(BoxLayout):
    accordion = ObjectProperty(None)
    table_form = ObjectProperty(None)
    search_box = ObjectProperty(None)
    search_input = ObjectProperty()
    search_results = ObjectProperty(None)
    col_value = ObjectProperty()
    table_value = ObjectProperty()

    def __init__(self, **kwargs):
        super(TableModifications, self).__init__(**kwargs)

    def show_form(self, table, type, *args):
        model = get_model(table)
        cols = model.__table__.columns._data.keys()
        self.table_form.clear_widgets()
        self.table_form.add_widget(MDLabel(font_style="Title",
                                           text=model.__qualname__,
                                           theme_text_color='Primary',
                                           size_hint_x=None,
                                           size_hint_y=None,
                                           height=self.height * 0.1,
                                           width=self.minimum_width,
                                           id='model'))
        for i, col in enumerate(cols):
            self.table_form.add_widget(MDLabel(font_style="Caption", text=col, theme_text_color='Primary'))
            if "id" == col:
                self.table_form.add_widget(MDTextField(hint_text=col, id=col, disabled=True))
            else:
                self.table_form.add_widget(MDTextField(hint_text=col, id=col))

        self.current_submit_button = MDRaisedButton(text=type, on_press=self.submit_form)
        self.table_form.add_widget(self.current_submit_button)

    def submit_form(self, *args):
        # add/edit/remove current_submit_button, current_table_form
        button = args[0]  # button na ktory sa kliklo
        fields = [item for item in button.parent.children if isinstance(item, MDTextField)]
        model_name = next((field.text for field in button.parent.children if field.id == "model"), None)
        if button.text == "Add":
            self.insert_row(model_name, fields)

    def insert_row(self, model_name, fields):
        model = get_model(model_name)
        model_kwargs = {field.id: field.text for field in fields if field.text != ""}
        try:
            session.add(model(**model_kwargs))
        except DataError:
            print(format_exc())
        session.commit()
        # TODO: clear fields

    def search(self):
        self.search_results.clear_widgets()

        rows = None
        table = get_model_by_tablename(self.table_value.text)
        col = getattr(table, self.col_value.text)
        search_input = self.search_input.text
        try:
            if col.property.columns[0].type.python_type is str:
                rows = session.query(table).filter(text(self.col_value.text + " @@ to_tsquery(:search_string)")).\
                    params(search_string=search_input).all()
            elif col.property.columns[0].type.python_type in [int, float]:
                rows = session.query(table).filter(
                    self.col_value.text + " = :search_string"). \
                    params(search_string=search_input).all()
        except Exception:
            print(format_exc())
        print(rows)
        if rows:
            for row in rows:
                attrs = [column.key for column in table.__table__.columns]
                values = [getattr(row, a) for a in attrs]
                attrs_and_vals = [str(a) + " = " + str(v) + "," for a, v in zip(attrs, values)]
                self.search_results.add_widget(TwoLineListItem(
                    text=str(getattr(row, self.col_value.text)),
                    secondary_text=" ".join(attrs_and_vals)))

    def clear_input(self):
        self.search_input.text = ""


class TableAccordionItem(MDAccordionItem):
    def __init__(self, **kwargs):
        super(TableAccordionItem, self).__init__(**kwargs)
        Clock.schedule_once(self.create_subitems)

    def create_subitems(self, dt):
        class_names = [get_model_by_tablename(name).__qualname__ for name in dal.engine.table_names() if
                       get_model_by_tablename(name) is not None]

        for name in class_names:
            item = MDAccordionSubItem(parent_item=self, text=name, on_release=partial(self.parent.parent.show_form, name, self.title))
            self.add_widget(item)


class MainApp(App):
    theme_cls = ThemeManager(primary_palette="BlueGrey")

    def build(self):
        layout = MainLayout()
        self.create_missing_days()
        self.theme_cls.theme_style = 'Dark'
        # Config.set("graphics", "window_state", "maximized")
        # Config.write()
        return layout

    def create_missing_days(self):
        today = date.today()
        s = dal.Session()
        most_recent = Day.get_most_recent_passed(s)
        if today > most_recent.date:
            dates = [most_recent.date + timedelta(days=x) for x in range((today - most_recent.date).days + 1)][1:]
            days = [Day(date=d) for d in dates]
            s.add_all(days)
            s.commit()
        s.close()


MainApp().run()
