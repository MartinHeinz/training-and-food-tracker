import re
from collections import namedtuple

import datetime
from kivy.lang import Builder
from kivy.properties import Clock, partial, StringProperty
from kivymd.textfields import MDTextField
from psycopg2.extras import NumericRange

Builder.load_file('text_fields.kv')


class MyTextField(MDTextField):

    Field = namedtuple("Field", ["name", "type", "value"])
    type = StringProperty("string")
    name = StringProperty("")

    def __init__(self, **kwargs):
        super(MyTextField, self).__init__(**kwargs)
        self.name = kwargs.pop("name", "")
        Clock.schedule_once(partial(self.set_attr, kwargs.get("hint_text", ""), kwargs.get("helper_text", "")))

    def set_attr(self, hint_text, helper_text, dt):
        if hint_text != "":
            self.hint_text = hint_text
            self._hint_lbl.text = hint_text
        if helper_text != "":
            self.helper_text = helper_text
            self._msg_lbl.text = helper_text

    def parse(self):
        return self.text

    def get_field(self):
        field = self.Field(self.name, self.type, self.parse())
        return field


class RangeField(MyTextField):

    pat = re.compile('([+-]?([0-9]*[.])?[0-9]+-[+-]?([0-9]*[.])?[0-9]+)|([+-]?([0-9]*[.])?[0-9]+\+)')
    type = StringProperty("range")

    def parse(self):
        result = re.match(self.pat, self.text)
        value = result.group(1) if result else None
        if value:
            if "-" in value:
                return list(map(int, value.split("-"))) + ["[]"]
            else:
                return list(map(int, value.strip("+"))) + [None] + ["[)"]

    def get_field(self):
        args = self.parse()
        if args is not None:
            field = self.Field(self.name, self.type, NumericRange(*args))
        else:
            field = self.Field(self.name, self.type, None)
        return field


class ArrayField(MyTextField):

    pat = re.compile('([^,;]*)[,;]*')
    type = StringProperty("array")

    def parse(self):
        result = re.findall(self.pat, self.text)
        return [val.strip() for val in result if val != ""]


class BooleanField(MyTextField):

    pat = re.compile('(0|1|True|False)')
    type = StringProperty("bool")

    def parse(self):
        result = re.match(self.pat, self.text)
        val = result.group(1) if result else None
        if val:
            return val in ["1", "True"]

    def get_field(self):
        field = self.Field(self.name, self.type, self.parse())
        return field


class DateField(MyTextField):

    pat = re.compile('(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$')
    type = StringProperty("date")

    def parse(self):
        result = re.match(self.pat, self.text)
        if result is not None:
            return datetime.date(*(map(int, result.groups()[-1::-1])))
        else:
            return None


class TimeField(MyTextField):  # TODO test

    pat = re.compile('(([01]\d|2[0-3]):([0-5]\d)|24:00)')
    type = StringProperty("date")

    def parse(self):
        result = re.match(self.pat, self.text)
        if result is not None:
            return datetime.datetime.strptime('03:55', '%H:%M').time()
        else:
            return None
