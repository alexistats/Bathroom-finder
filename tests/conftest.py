import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Application fixture using an in-memory SQLite database."""
    test_app = create_app("default")
    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
    )
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture
def sample_bathroom(db):
    from app.models.bathroom import Bathroom
    b = Bathroom(
        name="Test Toilet",
        address="1 Test St, Brantford, ON",
        latitude=43.14,
        longitude=-80.27,
        indoor_location="Ground floor, near entrance",
        floor="Ground",
        accessibility=True,
        gender_type="gender_neutral",
        hours_open="9am-5pm",
        is_verified=True,
        source="manual",
    )
    db.session.add(b)
    db.session.commit()
    yield b
    db.session.delete(b)
    db.session.commit()
