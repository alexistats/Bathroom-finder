import os
from flask import Flask
from .extensions import db, migrate
from .config import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    # Import models so Flask-Migrate can detect them
    from .models import Bathroom, Rating  # noqa: F401

    migrate.init_app(app, db)

    from .routes.main import main_bp
    from .routes.bathrooms import bathrooms_bp
    from .routes.ratings import ratings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(bathrooms_bp)
    app.register_blueprint(ratings_bp)

    return app
