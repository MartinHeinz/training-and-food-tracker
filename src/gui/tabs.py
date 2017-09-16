from kivy.properties import OptionProperty, Clock
from kivymd.icon_definitions import md_icons
from kivymd.tabs import MDTab, MDTabbedPanel


class ArrowTabbedPanel(MDTabbedPanel):
    def __init__(self, **kwargs):
        super(ArrowTabbedPanel, self).__init__(**kwargs)
        self.index = 0
        self._refresh_tabs()

    def add_widget(self, widget, **kwargs):
        """ Add tabs to the screen or the layout.
        :param widget: The widget to add.
        """
        if isinstance(widget, MDTab):
            if self.index == 0 and type(widget) != ArrowTab:
                ArrowTab.add_arrow_tabs(self)
            self.index += 1
            if self.index == 3:  # ?
                self.previous_tab = widget
            widget.index = self.index
            widget.parent_widget = self
            self.ids.tab_manager.add_widget(widget)
            if self.index == 3:
                self.ids.tab_manager.current = self.ids.tab_manager.screens[2].name
            self._refresh_tabs()
        else:
            super(MDTabbedPanel, self).add_widget(widget)


class ArrowTab(MDTab):

    direction = OptionProperty('right', options=['left', 'right'])

    def __init__(self, **kwargs):
        self.direction = kwargs.pop("direction", "right")
        super(ArrowTab, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.name = self.direction
        self.text = self.direction
        # header = next(h for h in self.parent_widget.ids.tab_bar.children if h.tab == self)
        # header.children[0].text = u'\u2794'

    def on_tab_press(self, *args):
        par = self.parent_widget
        current_tab = par.ids.tab_manager.current_screen
        if current_tab.name in ["left", "right"]:
            par.ids.tab_manager.current = next(tab.name for tab in par.ids.tab_manager.screens if tab.index == 3)
            par.ids.tab_manager.transition.direction = "right"
        elif self.direction == "left":
            if current_tab.index > 3:
                par.ids.tab_manager.current = next(tab.name for tab in par.ids.tab_manager.screens if tab.index == current_tab.index-1)
                par.ids.tab_manager.transition.direction = "left"
        elif self.direction == "right":
            if current_tab.index > 2:
                new_current = next((tab.name for tab in par.ids.tab_manager.screens if tab.index == current_tab.index+1), None)
                if new_current is not None:
                    par.ids.tab_manager.current = new_current
                    par.ids.tab_manager.transition.direction = "right"

    @classmethod
    def add_arrow_tabs(cls, panel):
        panel.add_widget(ArrowTab(direction="left"))
        panel.add_widget(ArrowTab(direction="right"))
