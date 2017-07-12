from sqlalchemy import Column, String
from src import dal
from functools import wraps


class MixinGetByName(object):
    name = Column(String)

    @classmethod
    def get_by_name(cls, session, name):
        return session.query(cls).filter(cls.name == name).all()


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
