from flask import Flask
from app.routes import api_bp
from app.error_handlers import register_error_handlers


def create_app():
    """ Creates a Flask app instance. """
    app = Flask(__name__)

    # Load configurations
    app.config.from_object('app.config.Config')

    # Register the Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    register_error_handlers(app)

    return app