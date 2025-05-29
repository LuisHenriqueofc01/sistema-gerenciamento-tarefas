from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Instâncias das extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Configurações de e-mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Importar modelos
    from app.models import models
    from app.models.models import User, ProcessModel, TaskTemplate, ProcessInstance, Task

    # Blueprints
    from .routes.auth import auth_bp
    from .routes.process import process_bp
    from .routes.views import views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(views_bp)

    # Iniciar o agendador
    from agendador import start_scheduler
    start_scheduler()

    return app
