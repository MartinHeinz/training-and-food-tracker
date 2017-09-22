import random
import string

from kivy.properties import Clock, ObjectProperty, partial, ListProperty
from kivy.uix.screenmanager import Screen
from kivymd.tabs import MDTab

from gui.forms import GoalForm
from gui.list_items import RightCheckboxListItem
from models.model import TrainingPlanHistory
from src import dal

session = None


class GoalsScreen(Screen):
    training_plan_list = ObjectProperty()
    tabbed_panel = ObjectProperty()
    toolbar = ObjectProperty()

    def __init__(self, **kwargs):
        super(GoalsScreen, self).__init__(**kwargs)
        global session
        if session is None:
            session = dal.Session()
        self.training_plan = None
        self.goal_forms = []
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        pass

    def on_enter(self, *args):
        self.fill_training_plan_list()
        super(GoalsScreen, self).on_enter(*args)
        contains = next((True for ar in self.toolbar.right_action_items if ar[0] == "content-save"), False)
        if not contains:
            self.toolbar.right_action_items.append(["content-save", lambda x: self.save_and_leave()])

    def on_pre_leave(self, *args):
        self.remove_save_button()
        self.training_plan = None
        self.goal_forms = []
        self.clear_tabs()
        self.training_plan_list.clear_widgets()
        session.rollback()

    def save_and_leave(self):
        self.save()
        self.training_plan = None
        self.goal_forms = []
        self.clear_tabs()
        self.manager.current = "default"

    def save(self):
        for form in self.goal_forms:
            form.submit()
        session.commit()

    def fill_training_plan_list(self):
        training_plans = TrainingPlanHistory.get_all(session)
        for tp in training_plans:
            start_date = "Start: {:%d, %b %Y }".format(tp.start)
            end_date = "    End: Ongoing" if getattr(tp, "end", None) is None else "    End: {:%d, %b %Y }".format(tp.end)
            secondary_text = start_date + end_date
            li = RightCheckboxListItem(text=tp.training_plan.name, secondary_text=secondary_text)
            self.training_plan_list.add_widget(li)
            li.checkbox.group = "training_plans"  # TODO test
            li.checkbox.bind(active=partial(self.show_training_plan, tp))

    def show_training_plan(self, training_plan, instance, value):
        if value:
            self.clear_tabs()
            for g in training_plan.goals:
                tab = MDTab(name=str(g.name), text=str(g.name))
                form = GoalForm(tph=training_plan, goal=g)
                self.goal_forms.append(form)
                tab.add_widget(form)
                form.remove.on_release = partial(self.remove_goal, form)
                form.set_fields(fields={
                    "name": g.name,
                    "achieved": g.achieved,
                    "start_date": g.start_date,
                    "end_date": g.end_date,
                    "notes": g.notes
                })
                self.tabbed_panel.add_widget(tab)
            self.tabbed_panel.add_widget(self.create_add_tab())
            self.training_plan = training_plan
        else:
            self.save()
            self.training_plan = None
            self.goal_forms = []
            self.clear_tabs()

    def create_add_tab(self):
        tab = MDTab(name="add", text="+")
        tab.on_tab_press = partial(self.on_tab_press, tab)
        return tab

    def on_tab_press(self, tab, *args):
        self.tabbed_panel.remove_widget(tab)
        new_goal_tab = MDTab(name=''.join(random.choices(string.ascii_uppercase + string.digits, k=5)),
                             text="New Goal")
        form = GoalForm(tph=self.training_plan)
        self.goal_forms.append(form)
        new_goal_tab.add_widget(form)
        form.remove.on_release = partial(self.remove_goal, form)
        self.tabbed_panel.add_widget(new_goal_tab)
        self.tabbed_panel.current = new_goal_tab.name
        self.tabbed_panel.previous_tab = new_goal_tab
        self.tabbed_panel.add_widget(tab)

    def clear_tabs(self):
        old_tabs = self.tabbed_panel.ids["tab_manager"].screens
        for tab in old_tabs[:]:
            self.tabbed_panel.remove_widget(tab)

    def remove_goal(self, goal_form):
        for g in self.training_plan.goals:
            if g is goal_form.goal:
                self.training_plan.goals.remove(g)
                break
        tab = goal_form.parent
        self.goal_forms.remove(goal_form)
        self.tabbed_panel.remove_widget(tab)

    def remove_save_button(self):
        self.toolbar.right_action_items[:] = [item for item in self.toolbar.right_action_items if
                                              item[0] != "content-save"]

