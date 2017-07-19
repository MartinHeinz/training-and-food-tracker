from src import dal, Base
from src.models.model import Exercise, Weight, TrainingPlanHistory, TrainingPlan, Tag, Equipment, Phase, \
    TrainingTemplate, Goal, TrainingTemplateExercise, TrainingSession, Day, BodyComposition, TrainingSessionExercise
from psycopg2.extras import NumericRange
import datetime
from itertools import chain

dal.connect()
Base.metadata.drop_all(dal.engine)
Base.metadata.create_all(dal.engine)
connection = dal.engine.connect()
session = dal.Session()

tags = [
    Tag(name="Upper", type="exercise", description="Upper body exercise."),
    Tag(name="Lower", type="exercise", description="Lower body exercise."),
    Tag(name="Chest", type="exercise", description="Chest exercise."),
    Tag(name="Main", type="exercise", description="Tag for main lifts, e.g. BP, DL, squat.")
]

equipment = [
    Equipment(name="Belt", description="Weight lifting belt. Use second to last hole."),
    Equipment(name="Box(55cm)", description="Box used for jumping, single leg squats, Goblet squat...")
]

session.add_all(tags)

exercises = [Exercise(name="Paused Bench Press",
                      tempo="21X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Classic normal grip width BP.",
                      tags=[tags[0], tags[2], tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Paused ATG Low Bar Squat",
                      tempo="21X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Classic ass to grass low bar squat.",
                      equipment=[equipment[0]],
                      tags=[tags[1], tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Deadlift",
                      tempo="10X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Classic deadlift",
                      equipment=[equipment[0]],
                      tags=[tags[1], tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Push Press",
                      tempo="10X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Classic dynamic over head press.",
                      tags=[tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),

             Exercise(name="Spoto Press(Normal Grip Width, 2 inch Above Chest)",
                      tempo="22X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Bench Press variation with pause above chest.",
                      tags=[tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Paused Incline Bench Press(30 degrees)",
                      tempo="21X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Incline variation of Bench Press. Use 6. hole on bench.",
                      tags=[tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Paused Close Grip Bench Press",
                      tempo="21X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Close grip variation of Bench Press",
                      tags=[tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Rack Press(Cluster)",
                      tempo="25X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Bench Press from pins, directly from chest. Release tension between reps(Cluster).",
                      tags=[tags[3]],
                      weight=Weight(RM=1,
                                    BW=False)),
             Exercise(name="Elevated Rack Press(2 inch Above Chest, Cluster)",
                      tempo="25X0",
                      # pause=NumericRange(0, 2),
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Bench Press from pins, from above chest. Release tension between reps(Cluster). Use adjustable bench.",
                      tags=[tags[3]],
                      weight=Weight(RM=1,
                                    BW=False))
             ]

conjugate = TrainingPlan(name="Conjugate",
                         description="Strength focused non-linear training program")

currPlan = TrainingPlanHistory(start=datetime.date(2017, 4, 3))
basicPhase = Phase(name="Basic", length=NumericRange(1, None, "[)"), description="Basic Conjugate template.")
templateOdd = TrainingTemplate(name="Conjugate Odd Week", description="6+1 template for odd weeks(Squat week).")
templateEven = TrainingTemplate(name="Conjugate Even Week", description="6+1 template for even weeks(Deadlift Week).")

conjugate.training_plan_history = [currPlan]
conjugate.phases = [basicPhase]
basicPhase.training_templates = [templateOdd, templateEven]

benchGoal5 = Goal(is_main=False, name="Bench Press Strength partial 5", exercise=exercises[8],
                  date=datetime.date(2017, 6, 28), kilogram=92.50, reps=1)
benchGoal4 = Goal(is_main=False, name="Bench Press Strength partial 4", exercise=exercises[7], next_partial=benchGoal5,
                  date=datetime.date(2017, 7, 5), kilogram=75.00, reps=1)
benchGoal3 = Goal(is_main=False, name="Bench Press Strength partial 3", exercise=exercises[6], next_partial=benchGoal4)
benchGoal2 = Goal(is_main=False, name="Bench Press Strength partial 2", exercise=exercises[5], next_partial=benchGoal3)
benchGoal1 = Goal(is_main=False, name="Bench Press Strength partial 1", exercise=exercises[4], next_partial=benchGoal2)
benchGoal = Goal(is_main=True, notes="Lockout strength(Top half strength), Weak point: 3 inch Above Chest",
                 name="Bench Press Strength main", exercise=exercises[0], next_partial=benchGoal1)

currPlan.goals = [benchGoal]

genericExercises = [Exercise(name="Squat",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(6, 10),
                             rep_range=NumericRange(2, 3),
                             notes="Generic squat exercise for template. Used in conjugate wave: 3 weeks 10/8/6 sets with 75/80/85% of 1RM. This exercise should be subbed by some variation.",
                             tags=[tags[1], tags[3]],
                             equipment=[equipment[0]],
                             weight=Weight(percentage_range=NumericRange(75, 85),
                                           BW=False)),
                    Exercise(name="Squat",
                             set_range=NumericRange(1, 1, "[]"),
                             rep_range=NumericRange(1, None),
                             notes="One set of AMRAP.",
                             tags=[tags[1]],
                             equipment=[equipment[0]],
                             weight=Weight(percentage_range=NumericRange(75, 85),
                                           BW=False)),
                    Exercise(name="Speed Deadlift variation",
                             tempo="10X0",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(6, 12),
                             rep_range=NumericRange(1, 1),
                             notes="Generic deadlift exercise for template. Used in conjugate dynamic lower. Do 6-12 singles of chosen variation with short pause",
                             equipment=[equipment[0]],
                             tags=[tags[1], tags[3]],
                             weight=Weight(percentage_range=NumericRange(75, 90),
                                           BW=False)),

                    Exercise(name="Dynamic Lower Accessory 1",
                             # pause=NumericRange(0, 10),
                             set_range=NumericRange(5, 5, "[]"),
                             rep_range=NumericRange(5, 5, "[]"),
                             notes="Generic template exercise for dynamic lower. 5x5 of chosen barbell accessory at 70-80% of 1RM. Usually squat accessory.",
                             tags=[tags[1]],
                             weight=Weight(percentage_range=NumericRange(70, 80),
                                           BW=False)),
                    Exercise(name="Dynamic Lower Accessory 1.1",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(5, 5, "[]"),
                             rep_range=NumericRange(10, 12, "[]"),
                             notes="Generic template exercise for dynamic lower. 5x10-12 of chosen accessory. Target weak point.",
                             tags=[tags[1]],
                             weight=Weight(percentage_range=NumericRange(70, 80),
                                           BW=False)),

                    Exercise(name="Dynamic Lower Accessory 2",
                             # pause=NumericRange(0, 10),
                             set_range=NumericRange(5, 5, "[]"),
                             rep_range=NumericRange(5, 5, "[]"),
                             notes="Generic template exercise for dynamic lower. 5x5 of chosen barbell accessory at 70-80% of 1RM. Usually deadlift accessory.",
                             tags=[tags[1]],
                             weight=Weight(percentage_range=NumericRange(70, 80),
                                           BW=False)),
                    Exercise(name="Dynamic Lower Accessory 2.1",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(5, 5, "[]"),
                             rep_range=NumericRange(10, 12, "[]"),
                             notes="Generic template exercise for dynamic lower. 5x10-12 of chosen accessory. Target weak point.",
                             tags=[tags[1]],
                             weight=Weight(percentage_range=NumericRange(70, 80),
                                           BW=False)),

                    Exercise(name="Dynamic Lower Accessory 3",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(5, 5, "[]"),
                             rep_range=NumericRange(10, 12, "[]"),
                             notes="Generic template exercise for dynamic lower. 5x10-12 of chosen accessory. Target weak point. Usually optional.",
                             tags=[tags[1]],
                             weight=Weight(BW=False)),
                    ]

exercisesForSession = [Exercise(name="Paused Front Squat",
                                tempo="22X0",
                                # pause=NumericRange(0, 60),
                                set_range=NumericRange(6, 10),
                                rep_range=NumericRange(2, 3),
                                notes="Grip: middle finger on grueling thumb over bar. This exercise is ATG squat. Used in conjugate wave as main movement: 3 weeks 10/8/6 sets with 75/80/85% of 1RM.",
                                tags=[tags[1], tags[3]],
                                weight=Weight(percentage_range=NumericRange(75, 85),
                                              BW=False)),
                       Exercise(name="Paused Front Squat",
                                tempo="22X0",
                                set_range=NumericRange(1, 1, "[]"),
                                rep_range=NumericRange(1, None),
                                notes="One set of AMRAP of ATG Paused Front Squat.",
                                tags=[tags[1]],
                                weight=Weight(percentage_range=NumericRange(75, 85),
                                              BW=False)),
                       Exercise(name="Speed Deadlift",
                                tempo="10X0",
                                # pause=NumericRange(0, 60),
                                set_range=NumericRange(6, 12),
                                rep_range=NumericRange(1, 1),
                                notes="Classic Deadlift. Performed as fast as possible.",
                                equipment=[equipment[0]],
                                tags=[tags[1], tags[3]],
                                weight=Weight(percentage_range=NumericRange(80, 90),
                                              BW=False)),

                       Exercise(name="Paused ATG High Bar Squat",
                                tempo="21X0",
                                # pause=NumericRange(0, 10),
                                set_range=NumericRange(5, 5, "[]"),
                                rep_range=NumericRange(5, 5, "[]"),
                                notes="Grip: Extended thumb width from end of grueling.",
                                tags=[tags[1]],
                                weight=Weight(percentage_range=NumericRange(70, 80),
                                              BW=False)),
                       Exercise(name="Dumbbell Squat",
                                tempo="2010",
                                # pause=NumericRange(0, 60),
                                set_range=NumericRange(5, 5, "[]"),
                                rep_range=NumericRange(10, 12, "[]"),
                                notes="ATG Squat performed with dumbbells held in each hand",
                                tags=[tags[1]],
                                weight=Weight(percentage_range=NumericRange(70, 80),
                                              BW=False)),

                       Exercise(name="Deficit Deadlift",
                                # pause=NumericRange(0, 10),
                                tempo="20X0",
                                set_range=NumericRange(5, 5, "[]"),
                                rep_range=NumericRange(5, 5, "[]"),
                                notes="Deadlift performed standing on 5kg + 25kg(old pink) plates(elevation = 3 inch).",
                                tags=[tags[1]],
                                weight=Weight(percentage_range=NumericRange(70, 80),
                                              BW=False)),
                       Exercise(name="Dumbbell Stiff Leg Deadlift",
                                # pause=NumericRange(0, 60),
                                tempo="2010",
                                set_range=NumericRange(5, 5, "[]"),
                                rep_range=NumericRange(10, 12, "[]"),
                                notes="Dumbbells are not touching ground. Legs are stiff but not locked.",
                                tags=[tags[1]],
                                weight=Weight(percentage_range=NumericRange(70, 80),
                                              BW=False)),

                       Exercise(name="Leg Press",
                                # pause=NumericRange(0, 60),
                                tempo="2010",
                                set_range=NumericRange(5, 5, "[]"),
                                rep_range=NumericRange(10, 12, "[]"),
                                notes="Feet are on upper part of machine, same width as squat. Do not lock knees at the top. Do not use full ROM.",
                                tags=[tags[1]],
                                weight=Weight(BW=False)),
                       ]
session.add_all(exercises)
session.add_all(genericExercises)
session.add_all(exercisesForSession)
session.add(conjugate)
session.commit()

dynamicLowerSquatSuperset = TrainingTemplateExercise.create_superset(session,
                                                                     [genericExercises[0].id, genericExercises[1].id],
                                                                     templateOdd.id)
dynamicLowerDeadlift = TrainingTemplateExercise.create_superset(session, [genericExercises[2].id], templateOdd.id)
dynamicLowerAccessory1 = TrainingTemplateExercise.create_superset(session,
                                                                  [genericExercises[3].id, genericExercises[4].id],
                                                                  templateOdd.id)
dynamicLowerAccessory2 = TrainingTemplateExercise.create_superset(session,
                                                                  [genericExercises[5].id, genericExercises[6].id],
                                                                  templateOdd.id)
dynamicLowerAccessory3 = TrainingTemplateExercise.create_superset(session, [genericExercises[7].id], templateOdd.id)

day = Day(date=datetime.date(2017, 7, 14),
          target_cal=NumericRange(2375, 2400),
          target_protein=NumericRange(160, 180),
          target_fibre=NumericRange(30, 40),
          body_composition=BodyComposition(weight=68.1))

training_session = TrainingSession(start=datetime.time(hour=8, minute=30),
                                   end=datetime.time(hour=9, minute=45),
                                   day=day,
                                   training_template=templateOdd)

session.add_all([day, training_session])
session.commit()

dynamicLowerSquatSupersetSession = TrainingSessionExercise.create_superset(session,
                                                                           [exercisesForSession[0].id,
                                                                            exercisesForSession[1].id],
                                                                           training_session.id)
dynamicLowerDeadliftSession = TrainingSessionExercise.create_superset(session, [exercisesForSession[2].id],
                                                                      training_session.id)
dynamicLowerAccessory1Session = TrainingSessionExercise.create_superset(session,
                                                                        [exercisesForSession[3].id,
                                                                         exercisesForSession[4].id],
                                                                        training_session.id)
dynamicLowerAccessory2Session = TrainingSessionExercise.create_superset(session,
                                                                        [exercisesForSession[5].id,
                                                                         exercisesForSession[6].id],
                                                                        training_session.id)
dynamicLowerAccessory3Session = TrainingSessionExercise.create_superset(session, [exercisesForSession[7].id],
                                                                        training_session.id)

session.add_all(
    chain(dynamicLowerSquatSuperset, dynamicLowerDeadlift, dynamicLowerAccessory1,
          dynamicLowerAccessory2, dynamicLowerAccessory3, dynamicLowerSquatSupersetSession, dynamicLowerDeadliftSession,
          dynamicLowerAccessory1Session, dynamicLowerAccessory2Session, dynamicLowerAccessory3Session))
session.commit()
