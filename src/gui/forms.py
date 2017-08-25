from kivy.lang import Builder
from kivy.properties import Clock, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeViewNode, TreeView, TreeViewLabel

from gui.text_fields import MyTextField
from functools import partial

from models.model import Exercise, Weight, Tag, Equipment, Set

Builder.load_file('forms.kv')


class Form(BoxLayout):

    def __init__(self, **kwargs):
        super(Form, self).__init__(**kwargs)
        self.fields = []

        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        for field in self.get_fields():
            self.fields.append(field)

    def parse(self):
        """ Parses fields, so they can be submitted."""
        result = []
        for field in self.get_fields():
            result.append(field.get_field())
        return result

    def submit(self):
        """ Submits form to database"""
        raise NotImplementedError()

    def add_field(self, name, hint_text, helper_text="", required=False):
        """ Creates and adds new field to form. """
        field = MyTextField(hint_text=hint_text, helper_text=helper_text, required=required)
        self.add_widget(field)
        self.fields[name] = field

    def get_fields(self):
        """ Yields all children, that as form fields. """
        for child in self.children:
            if isinstance(child, MyTextField):
                yield child


class ExerciseForm(Form):

    def __init__(self, **kwargs):
        self.dal = kwargs.pop("data_access_layer", None)
        if self.dal is None:
            raise Exception("No Data Access Layer provided.")
        super(ExerciseForm, self).__init__(**kwargs)
        Clock.schedule_once(self._set_error_fun)

    def _set_error_fun(self, dt):
        name_field = next(field for field in self.get_fields() if field.name == "name")
        name_field.bind(on_text_validate=self.checks_name_input,
                        on_focus=self.checks_name_input)

    def checks_name_input(self, *args):
        name_field = next(field for field in self.get_fields() if field.name == "name")
        exercises = Exercise.get_by_name(self.dal.Session(), name_field.text)
        if exercises:
            name_field.error = True
        else:
            name_field.error = False

    def submit(self):
        session = self.dal.Session()
        exercise = Exercise()
        exercise_col_names = Exercise.__table__.columns.keys()
        weight = Weight()
        weight_col_names = Weight.__table__.columns.keys()
        exercise.weight = weight

        for field in self.parse():
            # TODO odtialto skontrolovat. Vytvorit novy session, aby sa necommitli veci z left_panel?
            if field.name in exercise_col_names:
                setattr(exercise, field.name, field.value)
            elif field.name in weight_col_names:
                setattr(weight, field.name, field.value)
            elif field.name == "tag":
                for tag in field.value:
                    # ak tag este nieje v DB pridaj novy, inak iba prirad existujuci
                    tags = Tag.get_by_name(session, tag)
                    if tags:
                        exercise.tags.append(tags[0])
                    else:
                        exercise.tags.append(Tag(name=field.name, type="exercise"))
            elif field.name == "equipment":
                for equipment in field.value:
                    # ak equipment este nieje v DB pridaj novy, inak iba prirad existujuci
                    equipments = Equipment.get_by_name(session, equipment)
                    if equipments:
                        exercise.equipment.append(equipments[0])
                    else:
                        exercise.equipment.append(Tag(name=field.name))

        session.add(exercise)
        session.commit()
        return True

    # def dismiss(self):
    #     pass


class TrainingExerciseForm(Form):
    """ Form for TrainingExercise displaying. """

    set_tree = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.exercise = kwargs.pop("exercise", None)
        self.session = kwargs.pop("session", None)
        if self.exercise is None:
            raise Exception("Exercise not provided, use \"exercise=\" keyword argument.")
        if self.session is None:
            raise Exception("Session not provided, use \"session=\" keyword argument.")
        super(TrainingExerciseForm, self).__init__(**kwargs)
        Clock.schedule_once(self._setup_set_tree)

    def _setup_set_tree(self, dt):
        # self.set_tree.clear_widgets()
        for i, set in enumerate(self.exercise.sets):
            item = TreeViewLabel(text=self.format_label(set))
            self.set_tree.add_node(item)

    def format_label(self, set):
        return "Reps: {reps: <4} Weight: {weight: <8} {PR: <10} {AMRAP: <12}" \
            .format(reps=set.reps if set.reps is not None else "",
                    weight=set.weight if set.weight is not None else "",
                    PR="Is PR" if set.is_PR is not None and set.is_PR else "",
                    AMRAP="Is AMRAP" if set.is_AMRAP is not None and set.is_AMRAP else "")

    def submit(self):
        pass


class TrainingExerciseEditForm(TrainingExerciseForm):
    """ Form for TrainingExercise editing. """

    def __init__(self, **kwargs):
        self.adding_node = None
        super(TrainingExerciseEditForm, self).__init__(**kwargs)

    def _setup_set_tree(self, dt):
        self.set_tree.clear_widgets()
        for i, set in enumerate(self.exercise.sets):
            item = TreeViewLabel(text="Set " + str(i))
            set_node = TreeViewSet(exercise=self.exercise, set_id=i, session=self.session)
            self.set_tree.add_node(item)
            self.set_tree.add_node(set_node, item)
        self.adding_node = TreeViewAddSet()
        self.set_tree.add_node(self.adding_node)

    def delete_set(self, item):  # TODO test
        """ Deletes set(item) from set_tree and updates self.exercise.sets. """
        tree = item.parent
        item_label = item.parent_node
        tree.remove_node(item)
        tree.remove_node(item_label)
        self.exercise.sets.remove(item.set)
        print("delete set")

    def add_set(self):  # TODO test
        """ Adds set(item) to set_tree and updates self.exercise.sets. """
        self.set_tree.remove_node(self.adding_node)
        i = len(self.exercise.sets)
        self.exercise.sets.append(Set())
        item = TreeViewLabel(text="Set " + str(i))
        set_node = TreeViewSet(exercise=self.exercise, set_id=i, session=self.session)
        self.set_tree.add_node(item)
        self.set_tree.add_node(set_node, item)
        self.set_tree.add_node(self.adding_node)
        print("add set")

    def submit(self):
        self.exercise.is_optional = next(field.get_field().value for field in self.children if issubclass(field.__class__, MyTextField) and field.get_field().name == "is_optional")
        self.exercise.pause = next(field.get_field().value for field in self.children if issubclass(field.__class__, MyTextField) and field.get_field().name == "pause")
        for set_field in self.set_tree.children[:-1]:
            if type(set_field) is TreeViewLabel:
                set_field.nodes[0].update_set()
            elif type(set_field) is TreeViewSet:
                set_field.update_set()
        self.session.flush()
        return True

    def dismiss(self):
        self.session.expire(self.exercise)
        return True


class TreeViewSet(BoxLayout, TreeViewLabel):
    def __init__(self, **kwargs):
        self.exercise = kwargs.pop("exercise", None)
        self.set_id = kwargs.pop("set_id", None)
        self.session = kwargs.pop("session", None)
        if self.exercise is None:
            raise Exception("Exercise not provided, use \"exercise=\" keyword argument.")
        if self.set_id is None:
            raise Exception("Set id not provided, use \"set_id=\" keyword argument.")
        if self.session is None:
            raise Exception("Session not provided, use \"session=\" keyword argument.")
        self.set = self.exercise.sets[self.set_id]
        super(TreeViewSet, self).__init__(**kwargs)
        self.fields = {f.get_field().name: f for f in self.children if issubclass(f.__class__, MyTextField)}
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        self.update_set()
        self.update_text()
        for field in self.children:
            if issubclass(field.__class__, MyTextField):
                field.bind(text=self.update_text)

    def update_text(self, *args):
        self.parent_node.text = "Reps: {reps: <4} Weight: {weight: <8} {PR: <10} {AMRAP: <12}" \
            .format(reps=self.fields["reps"].get_field().value,
                    weight=self.fields["weight"].get_field().value,
                    PR="Is PR" if self.fields["is_PR"].get_field().value else "",
                    AMRAP="Is AMRAP" if self.fields["is_AMRAP"].get_field().value else "")

    def update_set(self):
        """ Updates set in session based on set fields. """
        for field in self.children:
            if issubclass(field.__class__, MyTextField):
                val = field.get_field().value
                setattr(self.set, field.get_field().name, val if val != "" else None)


class TreeViewAddSet(BoxLayout, TreeViewLabel):
    pass



