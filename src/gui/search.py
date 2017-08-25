from kivy.lang import Builder
from kivy.metrics import sp, dp
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, \
    StringProperty, Clock, partial, BoundedNumericProperty, ReferenceListProperty
from kivy.uix.textinput import TextInput
from kivymd.button import MDIconButton
from kivymd.card import MDCard
from kivymd.label import MDLabel
from kivymd.theming import ThemableBehavior

Builder.load_file('search.kv')


class SearchBox(MDCard):
    _search_hint = StringProperty()
    search_input = ObjectProperty(None)
    close_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._search_hint = kwargs.pop("hint_text", "")
        super(SearchBox, self).__init__(**kwargs)
        #Clock.schedule_once(partial(self.set_attr, hint_text))

    def set_attr(self, hint_text, dt=None):
        self._search_hint = hint_text

    def clear_input(self):
        self.search_input.text = ""

    def search(self):
        raise NotImplementedError()


class SearchTextInput(ThemableBehavior, TextInput):
    _hint_txt_color = ListProperty()
    _hint_lbl = ObjectProperty()
    _hint_lbl_font_size = NumericProperty(sp(16))
    _hint_y = NumericProperty(dp(10))

    def __init__(self, **kwargs):
        self._hint_lbl = MDLabel(font_style='Subhead',
                                 halign='left',
                                 valign='middle')
        super(SearchTextInput, self).__init__(**kwargs)


class CloseButton(MDIconButton):
    pass


class ValueBox(MDCard):
    text_value = ObjectProperty(None)
    _text_hint = StringProperty()

    def __init__(self, **kwargs):
        self._text_hint = kwargs.pop("hint_text", "")
        super(ValueBox, self).__init__(**kwargs)
        #Clock.schedule_once(partial(self.set_attr, hint_text))

    def set_attr(self, hint_text, dt=None):
        self._text_hint = hint_text

