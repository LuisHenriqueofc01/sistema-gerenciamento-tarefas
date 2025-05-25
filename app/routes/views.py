from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.models import ProcessInstance, ProcessModel, TaskTemplate, User, Task
from werkzeug.security import generate_password_hash
from app import db
from functools import wraps
from datetime import datetime, timedelta

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
@login_required
@admin_required
def criar_modelo():
    modelos = ProcessModel.query.order_by(ProcessModel.name).all()
    return render_template("criar_modelo.html", modelos=modelos)

@views_bp.route("/iniciar-processo")
@login_required
def iniciar_processo():
    processos = ProcessInstance.query.order_by(ProcessInstance.created_at.desc()).all()
    return render_template("iniciar_processo.html", processos=processos)

@views_bp.route("/kanban")
@login_required
def kanban():
    if current_user.is_admin:
        tarefas_com_processo = Task.query.filter(Task.process_id.isnot(None)).all()
        tarefas_sem_processo = Task.query.filter(Task.process_id.is_(None)).all()
    else:
        tarefas_com_processo = Task.query.filter(
            Task.assigned_user_id == current_user.id,
            Task.process_id.isnot(None)
        ).all()
        tarefas_sem_processo = Task.query.filter(
            Task.assigned_user_id == current_user.id,
            Task.process_id.is_(None)
        ).all()

    return render_template(
        "kanban.html",
        tarefas=tarefas_com_processo + tarefas_sem_processo,
        usuario=current_user
    )


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
            flash("Já existe um usuário com esse nome de usuário.", "danger")
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
        user_id = request.form.get("user_id")
        end_date_str = request.form.get("end_date")

        if not user_id:
            flash("Você deve selecionar um usuário.", "danger")
            return redirect(url_for("views.admin_panel"))

        assigned_user_id = int(user_id)

        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                flash("Data de vencimento inválida.", "danger")
                return redirect(url_for("views.admin_panel"))

        task = Task(
            title=title.strip(),
            description=description.strip(),
            assigned_user_id=assigned_user_id,
            process_id=None,
            order=0,
            status="pendente",
            start_date=datetime.utcnow(),
            end_date=end_date or datetime.utcnow() + timedelta(days=7)
        )

        db.session.add(task)
        db.session.commit()
        flash("Tarefa criada e atribuída com sucesso!", "success")

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
    flash("Status da tarefa atualizado com sucesso.", "success")
    return redirect(url_for("views.admin_panel"))

@views_bp.route("/admin/delete_task/<int:task_id>", methods=["POST"])
@login_required
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Tarefa excluída com sucesso.", "success")
    return redirect(url_for("views.admin_panel"))

@views_bp.route("/admin/promote/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"O usuário {user.username} agora é um administrador.", "success")
    return redirect(url_for("views.admin_panel"))

# ------------------------- EXCLUSÃO DE TAREFAS PELO KANBAN -------------------------
@views_bp.route("/excluir_tarefa/<int:task_id>", methods=["POST"])
@login_required
def excluir_tarefa(task_id):
    task = Task.query.get_or_404(task_id)

    if current_user.is_admin or task.assigned_user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash("Tarefa excluída com sucesso.", "success")
    else:
        flash("Você não tem permissão para excluir esta tarefa.", "danger")

    return redirect(url_for("views.kanban"))

# ------------------------- EXCLUSÃO DE PROCESSOS -------------------------
@views_bp.route("/process/delete/<int:processo_id>", methods=["POST"])
@login_required
@admin_required
def excluir_processo(processo_id):
    processo = ProcessInstance.query.get_or_404(processo_id)
    try:
        db.session.delete(processo)
        db.session.commit()
        flash("Processo excluído com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir processo: {str(e)}", "danger")
    return redirect(url_for("views.iniciar_processo"))

@views_bp.route("/processo/<int:processo_id>/tarefas")
@login_required
def listar_tarefas_do_processo(processo_id):
    processo = ProcessInstance.query.get_or_404(processo_id)
    tarefas = [{
        "id": t.id,
        "titulo": t.title,
        "status": t.status,
        "responsavel": t.assigned_user.name if t.assigned_user else "Ninguém"
    } for t in processo.tasks]
    return {"tarefas": tarefas}

@views_bp.route("/process/update/<int:processo_id>", methods=["POST"])
@login_required
@admin_required
def atualizar_processo(processo_id):
    processo = ProcessInstance.query.get_or_404(processo_id)
    data = request.get_json()

    try:
        processo.name = data.get("name", processo.name)
        processo.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d") if data.get("end_date") else None
        processo.responsavel_id = int(data["responsavel_id"])
        db.session.commit()
        return {"message": "Processo atualizado com sucesso."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro ao atualizar o processo: {str(e)}"}, 400

@views_bp.route("/processo/<int:processo_id>/atualizar-tarefas", methods=["POST"])
@login_required
@admin_required
def atualizar_tarefas_do_processo(processo_id):
    processo = ProcessInstance.query.get_or_404(processo_id)
    data = request.get_json()

    try:
        for tdata in data.get("tarefas", []):
            tarefa = Task.query.get(tdata["id"])
            if tarefa and tarefa.process_id == processo.id:
                tarefa.title = tdata["titulo"]
                tarefa.status = tdata["status"]
        db.session.commit()
        return {"message": "Tarefas atualizadas com sucesso."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro ao atualizar tarefas: {str(e)}"}, 400

# ------------------------- EXCLUSÃO DE MODELO -------------------------
@views_bp.route("/process/models/delete/<int:modelo_id>", methods=["POST"])
@login_required
@admin_required
def deletar_modelo_processo(modelo_id):
    modelo = ProcessModel.query.get_or_404(modelo_id)
    try:
        db.session.delete(modelo)
        db.session.commit()
        flash("Modelo excluído com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir modelo: {str(e)}", "danger")
    return redirect(url_for("views.criar_modelo"))

# ------------------------- CRIAÇÃO DE MODELO DE PROCESSO -------------------------
@views_bp.route("/process/models", methods=["POST"])
@login_required
@admin_required
def criar_modelo_processo():
    data = request.get_json()
    nome = data.get("name")
    tarefas = data.get("tasks", [])

    if not nome or not tarefas:
        return jsonify({"error": "Nome e tarefas são obrigatórios."}), 400

    try:
        modelo = ProcessModel(name=nome)
        db.session.add(modelo)
        db.session.flush()

        for i, t in enumerate(tarefas, start=1):
            nova = TaskTemplate(name=t["name"], order=i, model_id=modelo.id)
            db.session.add(nova)

        db.session.commit()
        return jsonify({
            "message": "Modelo criado com sucesso.",
            "modelo": {
                "id": modelo.id,
                "name": modelo.name
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar modelo: {str(e)}"}), 500

# ------------------------- LISTAGEM DE MODELOS (AJAX) -------------------------
@views_bp.route("/process/models/list")
@login_required
@admin_required
def listar_modelos_json():
    modelos = ProcessModel.query.order_by(ProcessModel.name).all()
    return jsonify([{"id": m.id, "name": m.name} for m in modelos])
