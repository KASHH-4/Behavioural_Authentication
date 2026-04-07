from flask import Flask

from app.api.routes import api_bp
from app.config import Config
from app.extensions import init_supabase
from app.services.logging_service import configure_logging


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    configure_logging(app)
    init_supabase(app)

    app.register_blueprint(api_bp)
    return app
