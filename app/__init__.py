from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Instâncias das extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Importar modelos (caminho atualizado para pasta models)
    from app.models import models
    from app.models.models import User, ProcessModel, TaskTemplate, ProcessInstance, Task

    # Blueprints
    from .routes.auth import auth_bp
    from .routes.process import process_bp
    from .routes.views import views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(views_bp)

    return app
