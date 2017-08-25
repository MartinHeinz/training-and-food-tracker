from src import dal, Base
from src.models.model import Exercise, Weight, TrainingPlanHistory, TrainingPlan, Tag, Equipment, Phase, \
    TrainingSchedule, Goal, Training, Day, BodyComposition, TrainingExercise, Meal, Food, MealFood, Recipe
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
basicPhase = Phase(name="Basic", length=NumericRange(1, None, "[)"), description="Basic Conjugate schedule.")
scheduleOdd = TrainingSchedule(name="Conjugate Odd Week", description="6+1 schedule for odd weeks(Squat week).")
scheduleEven = TrainingSchedule(name="Conjugate Even Week", description="6+1 schedule for even weeks(Deadlift Week).")

conjugate.training_plan_history = [currPlan]
conjugate.phases = [basicPhase]
basicPhase.training_schedules = [scheduleOdd, scheduleEven]

trainingDL = Training(name="Dynamic Lower",
                             description="Workout focused on speed work and lower body weak points.",
                             is_template=True,
                             is_first=True,  # TODO zmenit ked pribudnu ostatne templaty
                             )

trainingDU = Training(name="Dynamic Upper",
                             description="Workout focused on speed work and upper body weak points, mainly triceps.",
                             is_template=True)

trainingDL.next = trainingDU

scheduleOdd.trainings = [trainingDL, trainingDU]

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
                             set_range=NumericRange(1, None),
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

                    #############################################
                    Exercise(name="Bench Press",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(6, 10),
                             rep_range=NumericRange(2, 3),
                             notes="Generic bench press exercise for template. Used in conjugate wave: 3 weeks 10/8/6 sets with 75/80/85% of 1RM. This exercise should be subbed by some variation.",
                             tags=[tags[0], tags[2], tags[3]],
                             weight=Weight(percentage_range=NumericRange(75, 85),
                                           BW=False)),
                    Exercise(name="Bench Press",
                             set_range=NumericRange(1, None),
                             rep_range=NumericRange(1, None),
                             notes="One set of AMRAP.",
                             tags=[tags[0], tags[2], tags[3]],
                             weight=Weight(percentage_range=NumericRange(75, 85),
                                           BW=False)),
                    Exercise(name="Bench Press Barbell Accessory",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(3, 5, "[]"),
                             rep_range=NumericRange(3, 5, "[]"),
                             notes="Generic BP exercise for template. Used in conjugate dynamic upper. Use variation such as Floor Press, Spoto Press etc.",
                             tags=[tags[0], tags[2]],
                             weight=Weight(percentage_range=NumericRange(70, 80),
                                           BW=False)),

                    Exercise(name="Triceps Accessory 1",
                             # pause=NumericRange(0, 10),
                             set_range=NumericRange(4, 5, "[]"),
                             rep_range=NumericRange(10, 12, "[]"),
                             notes="Generic template exercise for dynamic upper. Used in first triceps superset.",
                             tags=[tags[0]]),
                    Exercise(name="Triceps Accessory 2",
                             # pause=NumericRange(0, 60),
                             set_range=NumericRange(4, 5, "[]"),
                             rep_range=NumericRange(10, 12, "[]"),
                             notes="Generic template exercise for dynamic upper. Used in second triceps superset.",
                             tags=[tags[0]])
                    ]

exercisesForSession = [Exercise(name="Paused Front Squat",
                                tempo="22X0",
                                # pause=NumericRange(0, 60),
                                set_range=NumericRange(6, 10, "[]"),
                                rep_range=NumericRange(2, 3, "[]"),
                                notes="Grip: middle finger on grueling thumb over bar. This exercise is ATG squat. Used in conjugate wave as main movement: 3 weeks 10/8/6 sets with 75/80/85% of 1RM.",
                                tags=[tags[1], tags[3]],
                                weight=Weight(percentage_range=NumericRange(75, 85),
                                              BW=False)),
                       Exercise(name="Paused Front Squat",
                                tempo="22X0",
                                set_range=NumericRange(1, None),
                                rep_range=NumericRange(1, None),
                                notes="One set of AMRAP of ATG Paused Front Squat.",
                                tags=[tags[1]],
                                weight=Weight(percentage_range=NumericRange(75, 85),
                                              BW=False)),
                       Exercise(name="Speed Deadlift",
                                tempo="10X0",
                                # pause=NumericRange(0, 60),
                                set_range=NumericRange(6, 12, "[]"),
                                rep_range=NumericRange(1, None),
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

exercisesForSession2 = [Exercise(name="Bench Press",
                                 tempo="10X0",
                                 # pause=NumericRange(0, 60),
                                 set_range=NumericRange(6, 10, "[]"),
                                 rep_range=NumericRange(2, 3, "[]"),
                                 notes="Classic Bench Press with no pause. Used in conjugate wave as main movement: 3 weeks 10/8/6 sets with 75/80/85% of 1RM.",
                                 tags=[tags[0], tags[2], tags[3]],
                                 weight=Weight(percentage_range=NumericRange(75, 85),
                                               BW=False)),
                        Exercise(name="Bench Press",
                                 tempo="10X0",
                                 # pause=NumericRange(0, 60),
                                 set_range=NumericRange(1, None),
                                 rep_range=NumericRange(1, None),
                                 notes="Classic Bench Press with no pause. Used in conjugate wave as main movement: 3 weeks 10/8/6 sets with 75/80/85% of 1RM. AMRAP.",
                                 tags=[tags[0], tags[2], tags[3]],
                                 weight=Weight(percentage_range=NumericRange(75, 85),
                                               BW=False)),
                        Exercise(name="Floor Press",
                                 tempo="11X0",
                                 # pause=NumericRange(0, 60),
                                 set_range=NumericRange(3, 5, "[]"),
                                 rep_range=NumericRange(3, 5, "[]"),
                                 notes="Chest accessory exercise in 3x3/3x5/5x3/5x5.",
                                 tags=[tags[0], tags[2]],
                                 weight=Weight(percentage_range=NumericRange(70, 80),
                                               BW=False)),

                        Exercise(name="Triceps Barbell Bench Press",
                                 tempo="1010",
                                 # pause=NumericRange(0, 10),
                                 set_range=NumericRange(4, 5, "[]"),
                                 rep_range=NumericRange(10, 12, "[]"),
                                 notes="Close grip bench press, focusing on triceps.",
                                 tags=[tags[0]]),
                        Exercise(name="Lying Dumbbell Triceps Extensions to Shoulders",
                                 tempo="2120",
                                 # pause=NumericRange(0, 60),
                                 set_range=NumericRange(4, 5, "[]"),
                                 rep_range=NumericRange(10, 12, "[]"),
                                 notes="Slow tempo with low weight.",
                                 tags=[tags[0]]),

                        Exercise(name="Standing Dumbbell French Press",
                                 # pause=NumericRange(0, 10),
                                 tempo="2010",
                                 set_range=NumericRange(4, 5, "[]"),
                                 rep_range=NumericRange(10, 12, "[]"),
                                 notes="Full Range French Press with one Dumbbell.",
                                 tags=[tags[0]]),
                        Exercise(name="Triceps Rope Pushdown",
                                 # pause=NumericRange(0, 60),
                                 tempo="1010",
                                 set_range=NumericRange(4, 5, "[]"),
                                 rep_range=NumericRange(10, 12, "[]"),
                                 notes="Performed on chain machine.",
                                 tags=[tags[0]]),
                        Exercise(name="Band Pushdowns",
                                 # pause=NumericRange(0, 60),
                                 tempo="10X0",
                                 set_range=NumericRange(4, 5, "[]"),
                                 rep_range=NumericRange(10, None),
                                 notes="AMRAP for pump.",
                                 tags=[tags[0]],
                                 weight=Weight(BW=False,
                                               band="Black Band")),
                        ]


session.add_all([scheduleOdd, scheduleEven])
session.add_all(exercises)
session.add_all(genericExercises)
session.add_all(exercisesForSession)
session.add_all(exercisesForSession2)
session.add(conjugate)
session.commit()

dynamicLowerSquatSuperset = TrainingExercise.create_superset(session,
                                                                     [genericExercises[0].id, genericExercises[1].id],
                                                                     trainingDL.id)
dynamicLowerDeadlift = TrainingExercise.create_superset(session, [genericExercises[2].id], trainingDL.id)
dynamicLowerAccessory1 = TrainingExercise.create_superset(session,
                                                                  [genericExercises[3].id, genericExercises[4].id],
                                                                  trainingDL.id)
dynamicLowerAccessory2 = TrainingExercise.create_superset(session,
                                                                  [genericExercises[5].id, genericExercises[6].id],
                                                                  trainingDL.id)
dynamicLowerAccessory3 = TrainingExercise.create_superset(session, [genericExercises[7].id], trainingDL.id)

dynamicUpperBPSuperset = TrainingExercise.create_superset(session,
                                                                     [genericExercises[8].id, genericExercises[9].id],
                                                                     trainingDU.id)
dynamicUpperBP = TrainingExercise.create_superset(session, [genericExercises[10].id], trainingDU.id)
dynamicUpperAccessory1 = TrainingExercise.create_superset(session,
                                                                  [genericExercises[11].id, genericExercises[11].id],
                                                                  trainingDU.id)
dynamicUpperAccessory2 = TrainingExercise.create_superset(session,
                                                                  [genericExercises[12].id, genericExercises[12].id,
                                                                   genericExercises[12].id],
                                                                  trainingDU.id)

day = Day(date=datetime.date(2017, 7, 14),
          target_cal=NumericRange(2375, 2400),
          target_protein=NumericRange(160, 180),
          target_fibre=NumericRange(30, 40),
          body_composition=BodyComposition(weight=67.6))

day2 = Day(date=datetime.date(2017, 7, 15),
           target_cal=NumericRange(2375, 2400),
           target_protein=NumericRange(160, 180),
           target_fibre=NumericRange(30, 40),
           body_composition=BodyComposition(weight=68.1))

training_session = Training(start=datetime.time(hour=8, minute=30),
                            end=datetime.time(hour=9, minute=45),
                            day=day,
                            template=trainingDL,
                            is_first=True  # TODO zmenit ked pribudnu ostatne sessions v tyzdni
                            )

training_session2 = Training(start=datetime.time(hour=8, minute=30),
                             end=datetime.time(hour=9, minute=45),
                             day=day2,
                             template=trainingDU
                             )

training_session.next = training_session2

session.add_all([day, training_session, day2, training_session2])
session.commit()

dynamicLowerSquatSupersetSession = TrainingExercise.create_superset(session,
                                                                           [exercisesForSession[0].id,
                                                                            exercisesForSession[1].id],
                                                                           training_session.id)
dynamicLowerDeadliftSession = TrainingExercise.create_superset(session, [exercisesForSession[2].id],
                                                                      training_session.id)
dynamicLowerAccessory1Session = TrainingExercise.create_superset(session,
                                                                        [exercisesForSession[3].id,
                                                                         exercisesForSession[4].id],
                                                                        training_session.id)
dynamicLowerAccessory2Session = TrainingExercise.create_superset(session,
                                                                        [exercisesForSession[5].id,
                                                                         exercisesForSession[6].id],
                                                                        training_session.id)
dynamicLowerAccessory3Session = TrainingExercise.create_superset(session, [exercisesForSession[7].id],
                                                                        training_session.id)

dynamicUpperBPSupersetSession = TrainingExercise.create_superset(session,
                                                                           [exercisesForSession2[0].id,
                                                                            exercisesForSession2[1].id],
                                                                        training_session2.id)
dynamicUpperBPSession = TrainingExercise.create_superset(session, [exercisesForSession2[2].id],
                                                                training_session2.id)
dynamicUpperAccessory1Session = TrainingExercise.create_superset(session,
                                                                        [exercisesForSession2[3].id,
                                                                         exercisesForSession2[4].id],
                                                                        training_session2.id)
dynamicUpperAccessory2Session = TrainingExercise.create_superset(session,
                                                                        [exercisesForSession2[5].id,
                                                                         exercisesForSession2[6].id,
                                                                         exercisesForSession2[7].id],
                                                                        training_session2.id)

foods1 = [Food(name="Skinless Salmon",
               cal=183,
               protein=19.9,
               carbs=0,
               fat=10.9,
               fibre=0),
          Food(name="Carrot",
               cal=41,
               protein=2.6,
               carbs=36.4,
               fat=2.0,
               fibre=2.8),
          Food(name="Green Peas (Frozen)",
               cal=77,
               protein=5.21,
               carbs=13.71,
               fat=0.37,
               fibre=4.2),
          Food(name="Extra Virgin Olive Oil",
               cal=884.1,
               protein=0,
               carbs=0,
               fat=100,
               fibre=0),
          Food(name="Butter",
               cal=716.8,
               protein=0.85,
               carbs=0.06,
               fat=81.11,
               fibre=0),
          Food(name="Semi-Skimmed Milk",
               cal=47,
               protein=3.33,
               carbs=4.83,
               fat=1.64,
               fibre=0),
          Food(name="Pesto Basilico",
               cal=310,
               protein=3.8,
               carbs=7.5,
               fat=31.4,
               fibre=1.5,
               brand="Panzani"),
          Food(name="Flour",
               cal=364,
               protein=10,
               carbs=76,
               fat=1,
               fibre=2.7),
          Food(name="Blueberries",
               cal=183,
               protein=19.9,
               carbs=0,
               fat=10.9,
               fibre=0),
          ]

foods2 = [Food(name="Lettuce",
               cal=14.8,
               protein=1.4,
               carbs=2.9,
               fat=0.2,
               fibre=1.3),
          Food(name="Tomatoes",
               cal=17,
               protein=0.9,
               carbs=3.9,
               fat=0.2,
               fibre=2.9),
          Food(name="Cucumber",
               cal=15.5,
               protein=0.7,
               carbs=3.6,
               fat=0.1,
               fibre=0.5),
          Food(name="Radish",
               cal=15.8,
               protein=0.7,
               carbs=3.4,
               fat=0.1,
               fibre=1.6)
          ]

foods3 = [Food(name="Egg",
               cal=155.1,
               protein=13,
               carbs=1.1,
               fat=11,
               fibre=0),
          Food(name="Sour Cream 14%",
               cal=153,
               protein=2.9,
               carbs=4.1,
               fat=14,
               fibre=4.2,
               brand="Rajo"),
          Food(name="Dijon Mustard",
               cal=149,
               protein=7.2,
               carbs=1.8,
               fat=11,
               fibre=0,
               brand="Dijona"),
          Food(name="Schwarzwald Ham",
               cal=239,
               protein=25,
               carbs=1,
               fat=15,
               fibre=0)
          ]

foods4 = [Food(name="Plain Yoghurt 3%",
               cal=65,
               protein=5,
               carbs=4.7,
               fat=2.8,
               fibre=0,
               brand="Rajo")
          ]

dinner1 = Meal(name="Dinner 1")  # Parent
# salmon = MealFood(amount=230)
# salmon.food = foods1[0]
# dinner1.foods.append(salmon)
# # ...
dinner1.add_food(foods1[0], 230)  # salmon 230g
dinner1.add_food(foods1[1], 360)  # carrot 360g
dinner1.add_food(foods1[2], 150)  # peas 150g
dinner1.add_food(foods1[3], 13.5)  # EVOO 1 tbsp
dinner1.add_food(foods1[4], 15)  # butter 15g
dinner1.add_food(foods1[5], 51.5)  # Semi-Skimmed Milk 50ml
dinner1.add_food(foods1[6], 50)  # pesto 50
dinner1.add_food(foods1[7], 3.91)  # flour 1/2 tbsp

salad = Recipe(name="Salad")
salad.add_food(session, foods2[0], 50)  # lettuce 50g
salad.add_food(session, foods2[1], 200)  # tomatoes 200g
salad.add_food(session, foods2[2], 100)  # cucumber 100g
salad.add_food(session, foods2[3], 50)  # lettuce 50g
salad.add_food(session, foods1[1], 20)  # carrot 20g

dinner2 = Meal(name="Dinner 2")  # Parent
dinner2.add_recipe(salad, 1)
dinner2.add_food(foods3[0], 464)  # egg 464g
dinner2.add_food(foods3[1], 40)  # sour cream 40g
dinner2.add_food(foods3[2], 18)  # dijon 3 tbsp
dinner2.add_food(foods3[3], 44)  # Schwarzwald Ham 44g

dinner3 = Meal(name="Dinner 3")  # Parent
dinner3.add_food(foods1[8], 250)  # blueberries 250g

snacks = Meal(foods="Snacks")  # Parent
snacks.add_food(foods4[0], 175)  # plain yoghurt 175g
snacks.add_food(foods2[1], 240)  # tomatoes 2 medium


meals = [dinner1, dinner2, dinner3, snacks]

day_food = Day(date=datetime.date(2017, 8, 25),
               target_cal=NumericRange(2475, 2500),
               target_protein=NumericRange(160, 180),
               target_fibre=NumericRange(30, 40),
               body_composition=BodyComposition(weight=69.0),
               meals=meals)



session.add_all(
    chain(dynamicLowerSquatSuperset, dynamicLowerDeadlift, dynamicLowerAccessory1, dynamicLowerAccessory2, dynamicLowerAccessory3,
          dynamicUpperBPSuperset, dynamicUpperBP, dynamicUpperAccessory1, dynamicUpperAccessory2,
          dynamicLowerSquatSupersetSession, dynamicLowerDeadliftSession, dynamicLowerAccessory1Session, dynamicLowerAccessory2Session, dynamicLowerAccessory3Session,
          dynamicUpperBPSupersetSession, dynamicUpperBPSession, dynamicUpperAccessory1Session, dynamicUpperAccessory2Session,
          day_food
          ))
session.commit()
