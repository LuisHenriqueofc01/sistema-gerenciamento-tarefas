from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# --------------------- USUÁRIO ---------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------- MODELO DE PROCESSO ---------------------
class ProcessModel(db.Model):
    __tablename__ = "process_models"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task_templates = db.relationship('TaskTemplate', backref='model', lazy=True, cascade="all, delete")


# --------------------- TEMPLATE DE TAREFA ---------------------
class TaskTemplate(db.Model):
    __tablename__ = "task_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('process_models.id'), nullable=False)


# --------------------- INSTÂNCIA DE PROCESSO ---------------------
class ProcessInstance(db.Model):
    __tablename__ = "process_instances"

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('process_models.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Campo adicionado

    responsavel_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsavel = db.relationship('User', backref='processos_responsaveis')

    tasks = db.relationship('Task', backref='process', lazy=True, cascade="all, delete")


# --------------------- TAREFA REAL ---------------------
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey('process_instances.id'), nullable=False)

    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_user = db.relationship('User', backref='tarefas_atribuidas')

    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="pendente")

    def is_completed(self):
        return self.status in ["concluída", "validada"]