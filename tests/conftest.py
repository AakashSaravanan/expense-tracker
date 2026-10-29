import os

# Must be set BEFORE the app is imported, so the app uses SQLite, not MySQL.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FLASK_SECRET_KEY"] = "test-secret-key"

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from config.database import db  # noqa: E402


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
