from collections import namedtuple
from difflib import get_close_matches

import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty, Clock, StringProperty, NumericProperty, AliasProperty, get_color_from_hex, \
    OptionProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivymd import color_definitions
from kivymd.button import MDIconButton
from kivymd.color_definitions import colors
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBodyTouch, TwoLineIconListItem, MDList, OneLineListItem, IRightBodyTouch, BaseListItem, \
    ContainerSupport, TwoLineRightIconListItem
from kivymd.list import TwoLineListItem
from kivymd.tabs import MDTab, MDTabbedPanel, MDTabHeader
from kivymd.textfields import MDTextField
import kivymd.material_resources as m_res
from kivymd.theming import ThemeManager
from kivymd.toolbar import Toolbar

from gui.forms import ExerciseForm, TrainingExerciseEditForm, TrainingExerciseForm
from gui.list_items import IconLeftWidget, LeftRightIconListItem
from gui.search import SearchBox, ValueBox
from gui.text_fields import MyTextField

from models.model import TrainingPlan, Training, TrainingExercise, Exercise, Tag, Equipment, Day, Set, \
    TrainingPlanHistory

from src import dal
from functools import partial

session = None  # dal.Session()


class TrainingPlanChooser(Screen):
    plan_chooser_list = ObjectProperty()
    create_list_item = ObjectProperty()

    def show_training_plan(self, training_plan=None, all_training_plans=None, *args):
        if training_plan:
            current_screen = next(screen for screen in self.manager.screens if isinstance(screen, PhaseChooser))
        else:
            current_screen = next(screen for screen in self.manager.screens if isinstance(screen, TrainingPlanCreator))
        self.manager.current = current_screen.name
        current_screen.show_layout(training_plan, all_training_plans)

    def on_pre_enter(self, *args):
        global session
        if session is None:
            session = dal.Session()

        training_plans = TrainingPlanHistory.get_all(session)
        for child in self.plan_chooser_list.children[:]:
            if child is not self.plan_chooser_list.children[-1]:
                self.plan_chooser_list.remove_widget(child)
        for tp in training_plans:
            icon = IconLeftWidget(icon="pencil")
            item = TwoLineIconListItem(text=tp.training_plan.name,
                                       secondary_text=tp.training_plan.description,
                                       on_press=partial(self.show_training_plan, tp, training_plans))
            item.add_widget(icon)
            self.plan_chooser_list.add_widget(item)

    def get_current(self):
        return TrainingPlan.get_current(session)


class TrainingPlanCreator(Screen):

    def show_layout(self, training_plan=None, all_training_plans=None):
        pass


class PhaseChooser(Screen):
    phase_chooser_list = ObjectProperty()

    def show_layout(self, training_plan=None, all_training_plans=None):
        for child in self.phase_chooser_list.children[:]:
            if child is not self.phase_chooser_list.children[-1]:
                self.phase_chooser_list.remove_widget(child)
        phases = training_plan.training_plan.phases
        for phase in phases:
            icon = IconLeftWidget(id="li_icon_" + str(phase.id),
                                  icon="pencil")
            item = TwoLineIconListItem(
                text=phase.name,
                secondary_text=phase.description,
                on_press=partial(self.show_phase, phase, phases)
            )
            item.add_widget(icon)
            self.phase_chooser_list.add_widget(item)

    def show_phase(self, phase=None, all_phases=None, *args):
        if phase:
            current_screen = next(screen for screen in self.manager.screens if isinstance(screen, TrainingScheduleChooser))
        else:
            current_screen = next(screen for screen in self.manager.screens if isinstance(screen, PhaseCreator))
        self.manager.current = current_screen.name
        current_screen.show_layout(phase, all_phases)


class PhaseCreator(Screen):
    def show_layout(self, training_plan=None, all_training_plans=None):
        pass


class TrainingScheduleChooser(Screen):
    schedule_chooser_list = ObjectProperty()
    create_list_item = ObjectProperty()

    def __init__(self, **kwargs):
        super(TrainingScheduleChooser, self).__init__(**kwargs)

    def show_layout(self, phase=None, all_phases=None):
        schedules = [s for p in all_phases for s in p.training_schedules]
        if not self.schedule_chooser_list.children:
            self.schedule_chooser_list.add_widget(self.create_list_item)
        for schedule in schedules:
            icon = IconLeftWidget(id="li_icon_" + str(schedule.id),
                                  icon="pencil",
                                  on_press=partial(self.show_list_of_existing, schedule, schedules))
            item = TwoLineIconListItem(
                text=schedule.name,
                secondary_text=schedule.description,
                on_press=partial(self.show_schedule, schedule, schedules)
            )
            item.add_widget(icon)
            self.schedule_chooser_list.add_widget(item)

    def show_list_of_existing(self, schedule, all_schedules, *args):
        current_screen = next(screen for screen in self.manager.screens if isinstance(screen, TrainingScheduleEditChooser))
        self.manager.current = current_screen.name
        current_screen.show_layout(schedule, all_schedules)

    def show_schedule(self, schedule=None, all_schedules=None, *args):
        if schedule:
            current_screen = next(screen for screen in self.manager.screens if isinstance(screen, TrainingTemplateSetUp))
        else:
            current_screen = next(screen for screen in self.manager.screens if isinstance(screen, TrainingScheduleCreator))
        self.manager.current = current_screen.name
        current_screen.show_layout(schedule, all_schedules)  # TODO implementovat v obidvoch classoch -> bud zobrazit creator alebo template z parametru na vyplnenie a browser strarych

    def on_leave(self, *args):
        for item in self.schedule_chooser_list.children[:]:
            self.schedule_chooser_list.remove_widget(item)


class TrainingScheduleCreator(Screen):

    def show_layout(self, schedule=None, schedules=None):  # TODO zobrazit form na vytvorenie schedule-u(name, desc, phase), nasledne vytvorenie jenotlivych templatov
        pass


class TrainingTemplateModifications(Screen):
    left_panel = ObjectProperty(None)
    right_panel = ObjectProperty(None)
    toolbar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TrainingTemplateModifications, self).__init__(**kwargs)
        self.training_sessions = []
        self.right_panel_inner_tabs = {}
        self.left_panel_tabs = []  # list of named tuples of training session GUI items each with .id .name, .date, .ex_list_items
        self.copied_exercise = None
        # self.alt_theme = HighlightTheme(accent_palette="Green", primary_palette="BlueGrey")
        # self.alt_theme.text_color = [0.78, 0.17, 0.17, 1]

    def on_enter(self, *args):
        contains = next((True for ar in self.toolbar.right_action_items if ar[0] == "content-save"), False)
        if contains:
            print("contains")
        else:
            self.toolbar.right_action_items.append(["content-save", lambda x: self.save_and_leave()])
            print("doesnt contain")

    def on_pre_leave(self, *args):  # TODO delete uncommitted, vyrobit vzdy na zaciatku uplne novy session
        # TODO vytvorit session v on_enter a zahodit session v on_leave, posielat ako parameter alebo vytvorit global
        # zmazat len ak bolo savenute -> poslat sem flag?
        self.remove_save_button()
        self.clear_tabs(self.right_panel)
        self.clear_tabs(self.left_panel)
        session.rollback()
        # for training in self.training_sessions:
        #     session.delete(training)
        # session.commit()
        # session.expunge_all()
        self.training_sessions = []

    def save_and_leave(self):
        self.save_training_session()
        self.manager.current = "default"

    def save_training_session(self, *args):
        names = [n.name.get_field().value for n in self.left_panel_tabs]
        dates = [d.date.get_field().value for d in self.left_panel_tabs]
        for i, ts_exercise in enumerate(self.training_sessions):
            ts_exercise.name = names[i] if names[i] != "" else None
            day = Day.get_by_date(session, dates[i]) if dates[i] is not None else None
            if day is not None:
                ts_exercise.day = day
            else:
                if dates[i] is not None:
                    ts_exercise.day = Day(date=dates[i])
        session.flush()
        session.commit()
        print("save")

    def show_layout(self, schedule, all_schedules):
        raise NotImplementedError

    def show_left_panel(self, training_sessions):
        TSessionTab = namedtuple("TSessionTab", ["id", "name", "date", "ex_list_items"])
        for training_session in training_sessions:
            outer_box = OuterBox(id=str(training_session.id))
            inputs_box = InputsBox(hint_text_left="Name", hint_text_right="Date",
                                   helper_text_left="Name of the training.",
                                   helper_text_right="Date in format: DD.MM.YYYY",
                                   text_left=getattr(training_session, "name", ""),
                                   text_right=getattr(training_session.day, "date", "") if training_session.day is not None else "")
            tab = MDTab(name=str(training_session.id), text=training_session.template.name)
            outer_box.search_layout.search_field.search = partial(self.search, outer_box.search_layout)
            outer_box.search_layout.search_field.close_button.on_release = \
                partial(self.clear_input_and_reset_tabs, outer_box.search_layout.search_field)
            outer_box.add_widget(inputs_box, 1)
            supersets = training_session.get_exercises()
            label_char = "A"
            li_supersets = []
            for i, superset in enumerate(supersets):
                li_superset = []
                for j, ex in enumerate(superset):
                    label_text = label_char + str(
                        j + 1) if ex.exercise.set_range.lower != 1 and ex.exercise.set_range.upper is not None else label_char + "+"
                    item = LeftRightIconListItem(text=label_text.ljust(4) + " " + ex.exercise.name,
                                                 secondary_text=ex.exercise.get_field_secondary_text(),
                                                 left_icon="pencil",
                                                 left_icon_id="li_icon_" + str(i) + "_" + str(j),
                                                 right_icon="delete",  # delete-forever
                                                 right_icon_id="li_icon_r_" + str(i) + "_" + str(j),
                                                 id=str(i) + "_" + str(j))
                    item.on_press = partial(self.insert_copied, item, training_session)
                    item.left_icon.on_press = partial(self.edit_exercise, item, training_session)
                    item.right_icon.on_press = partial(self.delete_exercise, item, training_session)
                    outer_box.ex_list.add_widget(item)
                    li_superset.append(item)
                li_supersets.append(li_superset)
                label_char = chr(ord(label_char) + 1)

            self.left_panel_tabs.append(TSessionTab(training_session.id,
                                                    inputs_box.left_field,
                                                    inputs_box.right_field,
                                                    li_supersets))
            tab.add_widget(outer_box)
            self.left_panel.add_widget(tab)

    def edit_exercise(self, source_item, training_session):
        """ Edit exercise inside self.left_panel(edit set number and set attributes, pause)"""
        number_of_superset, number_in_superset = list(map(int, source_item.id.split("_")))
        ex_to_edit = self.get_exercise_from_panel(number_of_superset, number_in_superset, training_session)
        content = TrainingExerciseEditForm(exercise=ex_to_edit, session=session, size_hint_y=None, pos_hint={"y": 0.15})
        dialog = MDDialog(title="Edit Exercise",
                          content=content,
                          size_hint=(.3, .95),
                          pos_hint={"x": 0.1},
                          auto_dismiss=False)

        def submit():
            if content.submit():
                dialog.dismiss()
                print("submitted")

        def dismiss():
            if content.dismiss():
                dialog.dismiss()
                print("dismissed")

        dialog.add_action_button("Submit",
                                 action=lambda *x: submit())
        dialog.add_action_button("Dismiss",
                                 action=lambda *x: dismiss())
        dialog.open()
        print("edit")

    def delete_exercise(self, source_item, training_session):  # TODO refresh labels(A1, A2...)
        """ Deletes item from left_panel and from training_session. """
        number_of_superset, number_in_superset = list(map(int, source_item.id.split("_")))
        ex_to_delete = self.get_exercise_from_panel(number_of_superset, number_in_superset, training_session)
        item_list = source_item.parent
        source_item.parent.remove_widget(source_item)
        if ex_to_delete.prev is None and ex_to_delete.superset_with is None:  # not a superset
            training_session.training_exercises.remove(ex_to_delete)
        elif ex_to_delete.prev is None and ex_to_delete.superset_with is not None:  # is first, but has next
            new_first = ex_to_delete.superset_with
            new_first.prev = None
            training_session.training_exercises[number_of_superset] = new_first
        elif ex_to_delete.prev is not None and ex_to_delete.superset_with is None:  # is last
            new_last = ex_to_delete.prev
            new_last.superset_with = None
        elif ex_to_delete.prev is not None and ex_to_delete.superset_with is not None:  # is in middle
            ex_to_delete.prev.superset_with = ex_to_delete.superset_with
        del ex_to_delete
        self.update_ex_list_ids(item_list, training_session)
        self.update_list_item_labels(item_list, training_session)
        # session.flush()?
        print("delete TE")

    def update_ex_list_ids(self, item_list, training_session):  # TODO test
        li_index = len(item_list.children)-1
        for i, superset_ex in enumerate(training_session.training_exercises):
            j = 0
            while superset_ex is not None:
                li = item_list.children[li_index]
                if type(li) != LeftRightIconListItem:
                    raise Exception("Wrong List Item Type.")
                li.id = "{i}_{j}".format(i=i, j=j)
                superset_ex = superset_ex.superset_with
                j += 1
                li_index -= 1

    def update_list_item_labels(self, item_list, training_session):
        li_index = len(item_list.children) - 1
        label_char = "A"
        for superset_ex in training_session.training_exercises:
            i = 1
            while superset_ex is not None:
                li = item_list.children[li_index]
                if type(li) != LeftRightIconListItem:
                    raise Exception("Wrong List Item Type.")
                name = (li.text.split(" ", 1)[1]).lstrip(" ")
                label = label_char + str(i) if superset_ex.exercise.set_range.lower != 1 and superset_ex.exercise.set_range.upper is not None else label_char + "+"
                li.text = label.ljust(4) + " " + name
                superset_ex = superset_ex.superset_with
                i += 1
                li_index -= 1
            label_char = chr(ord(label_char) + 1)

    def insert_copied(self, source_item, training_session):
        """ Insert copied exercise from self.copied_exercise, if it is not None and update self.training_sessions"""
        if self.copied_exercise is not None:
            self.copied_exercise.list_item.left_icon.icon = "content-copy"

            number_of_superset, number_in_superset = list(map(int, source_item.id.split("_")))

            superset_label = source_item.text.split()[0]
            source_item.text = superset_label.ljust(4) + " " + self.copied_exercise.exercise.name
            source_item.secondary_text = self.copied_exercise.exercise.get_field_secondary_text()
            ex = self.get_exercise_from_panel(number_of_superset, number_in_superset, training_session)
            ex.exercise = self.copied_exercise.exercise
            if ex.exercise.rep_range.upper is not None:
                sets = [Set(reps=ex.exercise.rep_range.upper) for _ in range(ex.exercise.set_range.upper)]
            else:
                sets = [Set(reps=ex.exercise.rep_range.lower) for _ in range(ex.exercise.set_range.lower)]
            ex.sets = sets
            session.flush()
            self.copied_exercise = None

    def get_exercise_from_panel(self, number_of_superset, number_in_superset, training_session):
        ex = training_session.training_exercises[number_of_superset]
        i = 0
        while ex is not None:
            if i == number_in_superset:
                return ex
            ex = ex.superset_with
            i += 1

    def search(self, search_layout):
        available_search_values = ["name", "tempo", "notes", "RM", "kilogram", "band", "tag", "equipment"]
        search_input = search_layout.get_search_field_value()
        search_by_field_value = search_layout.get_search_by_value()
        result_list = search_layout.get_result_list()
        result_list.clear_widgets()
        search_by_value = ""
        if search_by_field_value:
            search_result_list = get_close_matches(search_by_field_value, available_search_values)
            if search_result_list:
                search_by_value = search_result_list[0]
        self.reset_tab_colors(self.right_panel)
        item_create_ex = OneLineListItem(text="Create New Exercise",
                                         on_press=self.show_create_ex_dialog)
        result_list.add_widget(item_create_ex)
        if search_by_value in available_search_values:
            search_layout.set_search_by_value(search_by_value)
            if search_by_value == "tag":
                rows = Exercise.search_by_tag(session, search_input)
            elif search_by_value == "equipment":
                rows = Exercise.search_by_equipment(session, search_input)
            elif search_by_value in ["RM", "kilogram", "band"]:
                rows = Exercise.search_by_weight(session, search_input, search_by_value)
            else:
                rows = Exercise.search_by_attribute(session, search_input, search_by_value)
            for row in rows:
                item = LeftRightIconListItem(text=row.name,
                                             secondary_text=row.get_field_secondary_text(),
                                             left_icon="content-copy",
                                             left_icon_id="li_icon_" + str(row.id),
                                             right_icon="magnify",
                                             right_icon_id="li_icon_r_" + str(row.id),
                                             right_icon_on_press=partial(self.highlight_tabs, row))
                item.left_icon.on_press = partial(self.copy_exercise, item, row)
                result_list.add_widget(item)

    def show_create_ex_dialog(self, *args):
        """ Shows dialog for creation of new exercise."""
        content = ExerciseForm(data_access_layer=dal)
        dialog = MDDialog(title="Create Exercise",
                          content=content,
                          size_hint=(.3, .8),
                          pos_hint={"x": 0.1},
                          auto_dismiss=False)

        def submit():
            if content.submit():
                dialog.dismiss()
                print("submitted")

        dialog.add_action_button("Submit",
                                 action=lambda *x: submit())
        dialog.add_action_button("Dismiss",
                                 action=lambda *x: dialog.dismiss())
        dialog.open()

    def copy_exercise(self, li, exercise):
        """ Used to copy exercise from search list. """
        if self.copied_exercise is not None:
            self.copied_exercise.list_item.left_icon.icon = "content-copy"
        li.left_icon.icon = "content-duplicate"
        CopiedEx = namedtuple("CopiedEx", ["list_item", "exercise"])
        self.copied_exercise = CopiedEx(li, exercise)

    def clear_input_and_reset_tabs(self, field):  # TODO clear list?
        field.search_input.text = ""
        self.reset_tab_colors(self.right_panel)

    def get_tabs(self, panel):
        return panel.ids["tab_manager"].screens

    def reset_tab_colors(self, panel):
        normal_theme = App.get_running_app().theme_cls
        outer_tabs = self.get_tabs(panel)
        for outer_tab in outer_tabs:
            if outer_tab.children:
                headers = outer_tab.parent_widget.ids["tab_bar"].children
                my_header = next(h for h in headers if h.tab == outer_tab)
                my_header.text_color = normal_theme._get_text_color()
                inner_tabs = outer_tab.children[0].ids["tab_bar"].children
                for inner_tab in inner_tabs:
                    inner_tab.text_color = normal_theme._get_text_color()

    def highlight_tabs(self, exercise, *args):
        for tab in self.right_panel_inner_tabs:
            for ex in self.right_panel_inner_tabs[tab]:
                if ex.exercise.id == exercise.id:
                    headers = tab.parent_widget.ids["tab_bar"].children
                    my_header = next(h for h in headers if h.tab == tab)
                    my_header.text_color = [0.24, 0.74, 0.24, 1]
                    outer_header = next(t for t in tab.parent_widget.parent.parent_widget.ids["tab_bar"].children if
                                        t.tab.name == tab.parent_widget.parent.name)
                    outer_header.text_color = [0.24, 0.74, 0.24, 1]
                    # tab.theme_cls = self.alt_theme
                    # tab.parent_widget._refresh_tabs()

    def clear_tabs(self, panel):
        old_tabs = panel.ids["tab_manager"].screens
        for tab in old_tabs[:]:
            panel.remove_widget(tab)

    def show_right_panel(self, schedules):
        self.right_panel_inner_tabs = {}
        training_lists = []
        for i, schedule in enumerate(schedules):
            for template in schedule.trainings:
                if template.is_first:
                    for training in template.template_executions:
                        if training not in self.training_sessions:
                            training_lists.append(training)

        training_lists.sort(key=lambda t: getattr(t.day, "date", datetime.date(year=2100, month=1, day=1)))
        for i, training in enumerate(training_lists):
            outer_tab = MDTab(name="week_" + str(i + 1),
                              text=training.template.training_schedule.name + " " + str(i + 1))
            inner_panel = MDTabbedPanel()
            j = 0
            while training is not None:
                inner_tab = MDTab(name=outer_tab.name + "_" + str(j), text=training.template.name)
                self.right_panel_inner_tabs[inner_tab] = []
                scroll_view = ScrollView(id="scroll_view",
                                         do_scroll_x=False,
                                         size_hint=(1, 1),
                                         pos_hint={"top": 1})
                ex_list = MDList(id="inner_list" + str(training.id))
                scroll_view.add_widget(ex_list)
                supersets = training.get_exercises()
                label_char = "A"
                for superset in supersets:
                    for k, ex in enumerate(superset):
                        self.right_panel_inner_tabs[inner_tab].append(ex)
                        label_text = label_char + str(
                            k + 1) if ex.exercise.set_range.lower != 1 and ex.exercise.set_range.upper is not None else label_char + "+"
                        item = TwoLineListItem(id=str(ex.exercise.id),
                                               text=label_text.ljust(4) + " " + ex.exercise.name,
                                               on_press=partial(self.show_exercise_details, ex),
                                               secondary_text=ex.exercise.get_field_secondary_text())
                        item.height = dp(62)
                        ex_list.add_widget(item)  # TODO kazdemu itemu dat on_press pre zobrazenie cviku
                    label_char = chr(ord(label_char) + 1)
                inner_tab.add_widget(scroll_view)

                inner_panel.add_widget(inner_tab)
                training = training.next
                j += 1
            outer_tab.add_widget(inner_panel)
            self.right_panel.add_widget(outer_tab)

    def show_exercise_details(self, ex, *args):
        content = TrainingExerciseForm(exercise=ex, session=session)
        dialog = MDDialog(title=ex.exercise.name,
                          content=content,
                          size_hint=(.3, .9),
                          pos_hint={"x": 0.6},
                          auto_dismiss=False,
                          background_color=(0, 0, 0, 0),
                          )
        dialog.add_action_button("Dismiss",
                                 action=lambda *x: dialog.dismiss())

        dialog.open()

    def remove_save_button(self):
        self.toolbar.right_action_items[:] = [item for item in self.toolbar.right_action_items if
                                              item[0] != "content-save"]


class TrainingTemplateSetUp(TrainingTemplateModifications):

    def __init__(self, **kwargs):
        super(TrainingTemplateSetUp, self).__init__(**kwargs)
        self.training_sessions = []
        self.right_panel_inner_tabs = {}
        self.left_panel_tabs = []  # list of named tuples of training session GUI items each with .id .name, .date, .ex_list_items
        self.copied_exercise = None
        # self.alt_theme = HighlightTheme(accent_palette="Green", primary_palette="BlueGrey")
        # self.alt_theme.text_color = [0.78, 0.17, 0.17, 1]

    def show_layout(self, schedule, all_schedules):
        first_template = next((t for t in schedule.trainings if (t.is_template and t.is_first)), None)
        templates = []
        while first_template is not None:
            templates.append(first_template)
            first_template = first_template.next
        self.training_sessions = Training.create_training_sessions(session, templates)  # TREBA NAKONCI COMMITNUT
        self.show_left_panel(self.training_sessions)
        self.show_right_panel(all_schedules)


class TrainingScheduleEditChooser(Screen):  # TODO
    schedule_edit_chooser_list = ObjectProperty()

    def show_layout(self, schedule=None, all_schedules=None):
        schedule_execs = []
        for template in schedule.trainings:
            if template.is_first:
                for training in template.template_executions:
                    schedule_execs.append(training)

        schedule_execs.sort(key=lambda t: getattr(t.day, "date", datetime.date(year=2100, month=1, day=1)))

        for i, schedule_exec in enumerate(schedule_execs):
            icon = IconLeftWidget(id="li_icon_" + str(schedule.id),
                                  icon="pencil")
            t = getattr(schedule_exec, "name", None)
            d = getattr(schedule_exec.day, "date", None)
            item = TwoLineIconListItem(
                text=t if t is not None else "{name} {num}".format(name=schedule.name, num=i+1),
                secondary_text=str(d) if d is not None else "Date not provided.",
                on_press=partial(self.show_schedule, schedule_exec, all_schedules)
            )
            item.add_widget(icon)
            self.schedule_edit_chooser_list.add_widget(item)

    def show_schedule(self, schedule=None, all_schedules=None, *args):
        current_screen = next(screen for screen in self.manager.screens if isinstance(screen, TrainingScheduleEdit))
        self.manager.current = current_screen.name
        current_screen.show_layout(schedule, all_schedules)  # TODO implementovat v obidvoch classoch -> bud zobrazit creator alebo template z parametru na vyplnenie a browser strarych

    def on_leave(self, *args):
        for item in self.schedule_edit_chooser_list.children[:]:
            self.schedule_edit_chooser_list.remove_widget(item)


class TrainingScheduleEdit(TrainingTemplateModifications):  # TODO

    def show_layout(self, schedule_exec=None, schedules=None):
        print("show screen for week X editing")
        while schedule_exec is not None:
            self.training_sessions.append(schedule_exec)
            schedule_exec = schedule_exec.next
        self.show_left_panel(self.training_sessions)
        self.show_right_panel(schedules)

    def save_training_session(self, *args):
        names = [n.name.get_field().value for n in self.left_panel_tabs]
        dates = [d.date.get_field().value for d in self.left_panel_tabs]
        for i, ts_exercise in enumerate(self.training_sessions):
            ts_exercise.name = names[i] if names[i] != "" else None
            day = Day.get_by_date(session, dates[i]) if dates[i] is not None else None
            if day is not None:
                ts_exercise.day = day
            else:
                if dates[i] is not None:
                    ts_exercise.day = Day(date=dates[i])
        session.flush()
        session.commit()
        print("update")

    def on_pre_leave(self, *args):
        super().on_pre_leave(*args)
        self.remove_delete_button()

    def remove_delete_button(self):
        self.toolbar.right_action_items[:] = [item for item in self.toolbar.right_action_items if
                                              item[0] != "delete-forever"]

    def on_enter(self, *args):
        super(TrainingScheduleEdit, self).on_enter(*args)
        contains = next((True for ar in self.toolbar.right_action_items if ar[0] == "delete-forever"), False)
        if contains:
            print("contains")
        else:
            self.toolbar.right_action_items.append(["delete-forever", lambda x: self.delete_and_leave()])
            print("doesnt contain")

    def delete_and_leave(self):
        self.delete_training_session()
        self.manager.current = "default"
        print("delete and leave")

    def delete_training_session(self):
        for ts in self.training_sessions:
            session.delete(ts)
        session.commit()


class InputsBox(BoxLayout):
    left_field = ObjectProperty()
    right_field = ObjectProperty()

    def __init__(self, **kwargs):
        hint_left = kwargs.pop("hint_text_left", "")
        hint_right = kwargs.pop("hint_text_right", "")
        helper_text_left = kwargs.pop("helper_text_left", "")
        helper_text_right = kwargs.pop("helper_text_right", "")
        text_left = kwargs.pop("text_left", "")
        text_right = kwargs.pop("text_right", "")
        super(InputsBox, self).__init__(**kwargs)
        Clock.schedule_once(partial(self.set_attr,
                                    hint_left, hint_right, helper_text_left, helper_text_right, text_left, text_right))

    def set_attr(self, hint_left, hint_right, helper_text_left, helper_text_right, text_left, text_right, dt=None):
        self.left_field._hint_lbl.text = hint_left
        self.left_field.helper_text = helper_text_left
        self.left_field._msg_lbl.text = helper_text_left

        self.right_field._hint_lbl.text = hint_right
        self.right_field.helper_text = helper_text_right
        self.right_field._msg_lbl.text = helper_text_right

        self.left_field.text = text_left if text_left is not None else ""
        self.right_field.text = str(text_right) if text_right is not None else ""

    def show_date_picker(self):
        MDDatePicker(self.date_picker_callback).open()

    def date_picker_callback(self, date_obj):
        self.right_field.text = date_obj.strftime("%d.%m.%Y")


class SearchLayout(BoxLayout):
    search_field = ObjectProperty(None)
    search_by_field = ObjectProperty(None)
    result_list = ObjectProperty(None)

    result_list_height = NumericProperty()
    hint_text_left = StringProperty("")
    hint_text_right = StringProperty("")

    def __init__(self, **kwargs):
        self.hint_text_left = kwargs.pop("hint_text_left", "")
        self.hint_text_right = kwargs.pop("hint_text_right", "")
        rlh = kwargs.pop("result_list_height", None)
        super(SearchLayout, self).__init__(**kwargs)
        Clock.schedule_once(partial(self.set_attr, rlh))

    def set_attr(self, result_list_height, dt=None):
        self.search_field.set_attr(self.hint_text_left)
        self.search_by_field.set_attr(self.hint_text_right)
        if result_list_height is not None:
            self.result_list_height = result_list_height

    def set_search_field_value(self, value):
        self.search_field.search_input.text = value

    def get_search_field_value(self):
        return self.search_field.search_input.text

    def set_search_by_value(self, value):
        self.search_by_field.text_value.text = value

    def get_search_by_value(self):
        return self.search_by_field.text_value.text

    def get_result_list(self):
        return self.result_list


class OuterBox(StackLayout):
    ex_list = ObjectProperty(None)
    search_layout = ObjectProperty(None)


class HighlightTheme(ThemeManager):

    def _get_primary_dark(self):
        return get_color_from_hex(
            colors["Green"][self.primary_dark_hue])

    primary_dark = AliasProperty(_get_primary_dark,
                                 bind=('primary_palette', 'primary_dark_hue'))
