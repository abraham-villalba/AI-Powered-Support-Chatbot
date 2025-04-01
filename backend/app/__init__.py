from flask import Flask
from app.routes import api_bp

def create_app():
    app = Flask(__name__)

    # Load configurations
    # app.config.from_object('app.config.Config')

    # Register the Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    return app