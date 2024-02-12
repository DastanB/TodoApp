import pytest
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from models import Base, ToDos, Users
from routers.auth import bcrypt_context

SQL_ALCHEMY_DATABASE = 'sqlite:///./testdb.db'

engine = create_engine(
    SQL_ALCHEMY_DATABASE,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'test_dastan', 'id': 1, 'role': 'admin'}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = ToDos(
        title='Learn to code!',
        description='Need to learn everyday!',
        priority=5,
        complete=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username='test_dastan',
        email='dastan211298@gmail.com',
        first_name='Dastan',
        last_name='Baitursynov',
        role='admin',
        hashed_password=bcrypt_context.hash('1234'),
        phone_number='87772107915'
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()
