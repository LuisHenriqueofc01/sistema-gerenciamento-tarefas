from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import ProcessInstance, User, Task
from werkzeug.security import generate_password_hash
from app import db
from functools import wraps

views_bp = Blueprint("views", __name__)

# ------------------------- ADMIN CHECK -------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Acesso restrito ao administrador.", "danger")
            return redirect(url_for("views.index"))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------- PÁGINAS GERAIS -------------------------
@views_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("views.kanban"))
    return redirect(url_for("auth.login"))

@views_bp.route("/criar-modelo")
def criar_modelo():
    return render_template("criar_modelo.html")

@views_bp.route("/iniciar-processo")
def iniciar_processo():
    return render_template("iniciar_processo.html")

@views_bp.route("/kanban")
@login_required
def kanban():
    tarefas = Task.query.filter_by(assigned_user_id=current_user.id).all()
    return render_template("kanban.html", tarefas=tarefas, usuario=current_user)

@views_bp.route("/revisao-processo")
@login_required
def revisao_processo():
    return render_template("revisao.html")

@views_bp.route("/processo-finalizado")
@login_required
def processo_finalizado_pagina():
    return render_template("processo-finalizado.html")

@views_bp.route("/processo-finalizado/<int:process_id>")
@login_required
def processo_finalizado_com_id(process_id):
    processo = ProcessInstance.query.get_or_404(process_id)
    return render_template("processo-finalizado.html", processo=processo, usuario=current_user)

@views_bp.route("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("views.kanban"))
    return render_template("login.html")

# ------------------------- PAINEL ADMINISTRADOR -------------------------
@views_bp.route("/admin")
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    tasks = Task.query.all()
    return render_template("admin_panel.html", users=users, tasks=tasks)

@views_bp.route("/admin/create_user", methods=["POST"])
@login_required
@admin_required
def create_user():
    try:
        username = request.form["username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Usuário já existe com esse username.", "danger")
            return redirect(url_for("views.admin_panel"))
        if User.query.filter_by(email=email).first():
            flash("Já existe um usuário com esse e-mail.", "danger")
            return redirect(url_for("views.admin_panel"))

        new_user = User(username=username, name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuário criado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao criar usuário: {str(e)}", "danger")
    return redirect(url_for("views.admin_panel"))

@views_bp.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Usuário excluído com sucesso.", "success")
    return redirect(url_for("views.admin_panel"))

@views_bp.route("/admin/create_task", methods=["POST"])
@login_required
@admin_required
def create_task():
    try:
        title = request.form["title"]
        description = request.form["description"]
        assigned_user_id = int(request.form["user_id"])

        process = ProcessInstance.query.first()
        if not process:
            flash("Nenhum processo encontrado. Crie um processo antes de atribuir tarefas.", "danger")
            return redirect(url_for("views.admin_panel"))

        task = Task(
            title=title,
            description=description,
            assigned_user_id=assigned_user_id,
            process_id=process.id,
            order=1
        )
        db.session.add(task)
        db.session.commit()
        flash("Tarefa atribuída com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao criar tarefa: {str(e)}", "danger")
    return redirect(url_for("views.admin_panel"))

@views_bp.route("/admin/update_task_status/<int:task_id>", methods=["POST"])
@login_required
@admin_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = request.form["status"]
    db.session.commit()
    flash("Status atualizado.", "success")
    return redirect(url_for("views.admin_panel"))

@views_bp.route("/admin/promote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"O usuário {user.username} agora é administrador.", "success")
    return redirect(url_for("views.admin_panel"))
