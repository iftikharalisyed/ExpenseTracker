import pytest
from app import app as flask_app
from database.db import get_db, init_db


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.app_context():
        init_db()
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_user_id():
    """Returns the id of the seeded demo user."""
    db = get_db()
    row = db.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
    db.close()
    return row["id"]


@pytest.fixture
def empty_user_id():
    """Creates a user with no expenses and returns their id."""
    from database.db import create_user
    uid = create_user("Empty User", "empty@test.com", "password123")
    yield uid
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (uid,))
    db.commit()
    db.close()
