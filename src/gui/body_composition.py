import datetime
from kivy.properties import Clock, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.date_picker import MDDatePicker

from models.model import Day
from src import dal

session = None


class BodyCompositionScreen(Screen):

    toolbar = ObjectProperty()
    form = ObjectProperty()

    def __init__(self, **kwargs):
        super(BodyCompositionScreen, self).__init__(**kwargs)
        global session
        if session is None:
            session = dal.Session()
        self.day = None
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.set_date_field(datetime.date.today())

    def on_enter(self, *args):
        super(BodyCompositionScreen, self).on_enter(*args)
        if self.day is None:
            self.day = Day.get_by_date(session, datetime.date.today())
        self.form.day = self.day
        self.form.update_fields()
        self.set_date_field(self.day.date)
        contains = next((True for ar in self.toolbar.right_action_items if ar[0] == "content-save"), False)
        if not contains:
            self.toolbar.right_action_items.append(["content-save", lambda x: self.save_and_leave()])

    def on_pre_leave(self, *args):
        self.remove_save_button()
        session.rollback()

    def remove_save_button(self):
        self.toolbar.right_action_items[:] = [item for item in self.toolbar.right_action_items if
                                              item[0] != "content-save"]

    def save_and_leave(self):
        self.save()
        self.manager.current = "default"

    def save(self):
        self.form.submit()
        session.commit()

    def change_day(self):
        date_field_value = self.date_field.get_field().value
        new_day = Day.get_by_date(session, date_field_value)
        if new_day is None:
            new_day = self.get_day_from_session(date_field_value)
        if date_field_value is not None and date_field_value != self.day.date:
            if new_day is not None:
                self.day = new_day
            elif new_day is None:
                self.day = Day(date=self.date_field.get_field().value)
                session.add(self.day)
            self.form.submit()
            self.form.day = self.day
            self.form.update_fields()
            self.set_date_field(self.day.date)

    def get_day_from_session(self, date):
        for instance in session.new:
            if isinstance(instance, Day) and instance.date == date:
                return instance
        return None

    def show_date_picker(self):
        MDDatePicker(self.date_picker_callback).open()

    def date_picker_callback(self, date_obj):
        self.set_date_field(date_obj)
        self.change_day()

    def set_date_field(self, date):
        self.date_field.text = date.strftime("%d.%m.%Y")
