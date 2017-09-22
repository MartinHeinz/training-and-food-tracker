from dateutil.tz import tz
from kivy.properties import ObjectProperty, Clock, StringProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeViewLabel, TreeViewNode
from kivymd.selectioncontrols import MDCheckbox

import matplotlib.pyplot as plt
from libs.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.dates as mdates
from matplotlib import ticker
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
from matplotlib.ticker import FormatStrFormatter

from models.model import Day
from src import dal

session = None


class DataVisualizationScreen(Screen):

    toolbar = ObjectProperty(None)
    nav_layout = ObjectProperty()
    tree = ObjectProperty()
    plot = ObjectProperty()

    def __init__(self, **kwargs):
        super(DataVisualizationScreen, self).__init__(**kwargs)
        global session
        if session is None:
            session = dal.Session()
        Clock.schedule_once(self._finish_init)

    def on_pre_leave(self, *args):
        self.remove_drawer_button()
        session.close()  # TODO test

    def _finish_init(self, dt):
        self._add_weight_and_cal_nodes()
        self._add_exercise_nodes()
        self._add_goal_nodes()
        self.fig, self.ax = plt.subplots()
        # self.fig.patch.set_facecolor((0.1875, 0.1875, 0.1875))
        self.plot.add_widget(FigureCanvasKivyAgg(figure=plt.gcf()))  # self.fig

    def _add_weight_and_cal_nodes(self):  # TODO
        sub_root = self.tree.add_node(TreeViewDataSelectionRoot(text="Weight & Calories"))
        w = self.tree.add_node(TreeViewDataSelection(text='Weight', sub_root=sub_root), sub_root)
        w.show.bind(active=partial(self.toggle_active_weight, sub_root))
        w.correlation.bind(active=self.update_correlation)
        self.tree.add_node(TreeViewDataSelection(text='Calories', sub_root=sub_root), sub_root)
        self.tree.add_node(TreeViewDataSelection(text='Target Calories', sub_root=sub_root), sub_root)

    def toggle_active_weight(self, sub_root, instance, value, lines={}):  # TODO
        if value:
            days = session.query(Day).all()
            data = []
            for day in days:
                weight = getattr(day.body_composition, "weight", None)
                date = getattr(day, "date")
                if date is None or weight is None:
                    continue
                data.append((date, weight))

            data.sort(key=lambda pair: pair[0])
            dates, weights = zip(*data)
            lines["weight"] = self.ax.plot(dates, weights, "o-")

            self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
            self.ax.yaxis.set_major_formatter(FormatStrFormatter(''))
            self.ax.yaxis.set_minor_formatter(FormatStrFormatter('%.1f'))
            self.ax.yaxis.grid(True, "major")

            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
            self.ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=MO))
            self.ax.grid(True, "minor", linestyle="dashed")

            self.fig.autofmt_xdate()
        else:
            lines["weight"].pop(0).remove()
        self.fig.canvas.draw_idle()

    def update_correlation(self, instance, value):  # TODO
        print("show correlation")

    def _add_exercise_nodes(self):  # TODO
        sub_root = self.tree.add_node(TreeViewDataSelectionRoot(text="Exercises"))
        self.tree.add_node(TreeViewDataAddExercise(), sub_root)

    def _add_goal_nodes(self):  # TODO
        pass

    def on_enter(self, *args):
        contains = next((True for ar in self.toolbar.right_action_items if ar[0] == "menu"), False)
        if contains:
            print("contains")
        else:
            self.toolbar.right_action_items.append(["menu", lambda x: self.nav_layout.toggle_nav_drawer()])
            print("doesnt contain")

    def remove_drawer_button(self):
        self.toolbar.right_action_items[:] = [item for item in self.toolbar.right_action_items if
                                              item[0] != "menu"]


class TreeViewDataSelection(BoxLayout, TreeViewNode):  # TODO
    text = StringProperty("Node")
    sub_root = ObjectProperty()
    show = ObjectProperty()
    correlation = ObjectProperty()

    def __init__(self, **kwargs):
        super(TreeViewDataSelection, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.sub_root.bind_child_state_change(self, False)

    def toggle_show(self):
        self.show.active = not self.show.active

    def set_show_state(self, value, rebind):
        if rebind:
            self.sub_root.bind_child_state_change(self, True)
            self.show.active = value
            self.sub_root.bind_child_state_change(self, False)
        else:
            self.show.active = value

    def is_active(self):
        return self.show.active


class TreeViewDataSelectionRoot(BoxLayout, TreeViewNode):  # TODO
    text = StringProperty("Sub Root")
    show_hide_all = ObjectProperty()

    def __init__(self, **kwargs):
        super(TreeViewDataSelectionRoot, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.show_hide_all.on_press = self.toggle_children_checkboxes

    def set_checkbox_state(self, value):
        self.show_hide_all.active = value

    def bind_child_state_change(self, child, unbind=False):
        if unbind:
            child.show.unbind(active=self.child_state_change)
        else:
            child.show.bind(active=self.child_state_change)

    def child_state_change(self, instance, value):
        node_values = [n.is_active() for n in self.nodes if n.show != instance]
        node_values.append(value)
        all_inactive = all([not a for a in node_values])
        active = self.show_hide_all.active
        if all_inactive:
            self.set_checkbox_state(False)
        else:
            self.set_checkbox_state(True)
        pass

    def toggle_checkbox(self):
        self.show_hide_all.active = not self.show_hide_all.active

    def toggle_children_checkboxes(self):
        state = self.show_hide_all.active
        for n in self.nodes:
            n.set_show_state(state, True)


class TreeViewDataAddExercise(BoxLayout, TreeViewNode):  # TODO
    text = StringProperty("Add Exercise")


class MyMDCheckbox(MDCheckbox):
    pass
