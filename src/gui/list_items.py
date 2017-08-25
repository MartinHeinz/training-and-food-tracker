from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, Clock
from kivymd.button import MDIconButton
from kivymd.list import TwoLineRightIconListItem, TwoLineIconListItem, BaseListItem, IRightBodyTouch, ILeftBodyTouch
import kivymd.material_resources as m_res

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
