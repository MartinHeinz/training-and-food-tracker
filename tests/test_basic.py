# -*- coding: utf-8 -*-

# from .context import src
from src.models.model import *
from psycopg2.extras import NumericRange


class TestBasic:
    """Basic test cases."""

    def test_db_lookup(self, db_session):
        ex = Exercise(name="Paused Bench Press",
                      tempo="21X0",
                      set_range=NumericRange(6, 8),
                      rep_range=NumericRange(1, 3),
                      notes="Classic normal grip width BP.",
                      weight=Weight(RM=1,
                                    BW=False))
        db_session.add(ex)
        assert 1 == db_session.query(Exercise).count()

    def test_db_is_rolled_back(self, db_session):
        assert 0 == db_session.query(Exercise).count()

    def test_get_by_name(self, db_session):
        exercises = [Exercise(name="1"), Exercise(name="1"), Exercise(name="2")]
        db_session.add_all(exercises)
        assert len(Exercise.get_by_name(db_session, "1")) == 2

