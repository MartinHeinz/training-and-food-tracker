# -*- coding: utf-8 -*-

import pytest
from sqlalchemy.orm import scoped_session
from src import dal, Base


@pytest.fixture(scope='session')
def session(request):
    dal.connect()

    dal.Session = scoped_session(dal.Session)
    dal.session = dal.Session()
    dal.Session.registry.clear()

    request.addfinalizer(Base.metadata.drop_all)
    return dal.session


@pytest.fixture(scope='function')
def db_session(request, session):
    request.addfinalizer(session.rollback)
    return session