from sqlalchemy import Column, String, func, and_
from src import dal
from functools import wraps


class MixinGetByName(object):
    name = Column(String)

    @classmethod
    def get_by_name(cls, session, name):
        return session.query(cls).filter(cls.name == name).all()


class MixinSearch(object):

    @classmethod
    def search_by_attribute(cls, session, search_string, field):
        words = " & ".join(search_string.split())
        return session.query(cls). \
            filter(func.to_tsvector('english', getattr(cls, field)).match(words, postgresql_regconfig='english')).all()

    @classmethod
    def get_closest_matches(cls, session, search_value, field, delta):
        col = getattr(cls, field)
        return session.query(cls). \
            filter(and_(col >= search_value-delta, col <= search_value+delta))


def transaction(fn):
    """ By moving `session.commit()` into a decorator, more flexibility for
    testing is achieved. If you pass in persist=False, `session.commit()` is
    never called and the changes are never persisted to the DB.
    Usage:
    @transaction
    def my_function():
        ...
    """

    @wraps(fn)
    def wrapper(*a, **kw):
        persist = kw.pop('persist', True)
        r = fn(*a, **kw)
        if persist is True:
            dal.session.commit()
        return r
    return wrapper
