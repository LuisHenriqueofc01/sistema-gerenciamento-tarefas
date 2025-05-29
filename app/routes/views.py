from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.models import ProcessInstance, ProcessModel, TaskTemplate, User, Task
from app import db, mail  # já aproveita para importar o mail aqui
from flask_mail import Message
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
        tarefas = Task.query.all()
    else:
        tarefas = Task.query.filter(Task.assigned_user_id == current_user.id).all()

    tarefas_pendentes = [t for t in tarefas if t.status.lower() == "pendente"]
    tarefas_progresso = [t for t in tarefas if t.status.lower() == "em progresso"]
    tarefas_concluidas = [t for t in tarefas if t.status.lower() == "concluída"]

    return render_template(
        "kanban.html",
        tarefas_pendentes=tarefas_pendentes,
        tarefas_progresso=tarefas_progresso,
        tarefas_concluidas=tarefas_concluidas,
        usuario=current_user
    )

@views_bp.route("/excluir_tarefa/<int:task_id>", methods=["POST"])
@login_required
def excluir_tarefa(task_id):
    tarefa = Task.query.get_or_404(task_id)

    if not current_user.is_admin and tarefa.assigned_user_id != current_user.id:
        flash("Você não tem permissão para excluir esta tarefa.", "danger")
        return redirect(url_for("views.kanban"))

    try:
        db.session.delete(tarefa)
        db.session.commit()
        flash("Tarefa excluída com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir tarefa: {str(e)}", "danger")

    return redirect(url_for("views.kanban"))

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

# ------------------------- ALTERAÇÃO DE SENHA -------------------------
@views_bp.route("/alterar-senha", methods=["GET", "POST"])
@login_required
def change_password_page():
    if request.method == "POST":
        senha_atual = request.form.get("current_password")
        nova_senha = request.form.get("new_password")
        confirmar_senha = request.form.get("confirm_password")

        if not current_user.check_password(senha_atual):
            flash("Senha atual incorreta.", "danger")
        elif nova_senha != confirmar_senha:
            flash("Nova senha e confirmação não coincidem.", "danger")
        else:
            current_user.set_password(nova_senha)
            db.session.commit()
            flash("Senha alterada com sucesso!", "success")
            return redirect(url_for("views.index"))

    return render_template("alterar_senha.html")

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
        username = request.form["new_username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["new_password"]

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
    ADMIN_PRINCIPAL_ID = 1
    if user_id == ADMIN_PRINCIPAL_ID:
        flash("O usuário administrador principal não pode ser excluído.", "danger")
        return redirect(url_for("views.admin_panel"))

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
            status="Pendente",
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
    task.status = request.form["status"].capitalize()
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

# ------------------------- MODELOS DE PROCESSO -------------------------
@views_bp.route("/process/models/<int:modelo_id>", methods=["GET"])
@login_required
@admin_required
def carregar_modelo(modelo_id):
    modelo = ProcessModel.query.get_or_404(modelo_id)
    tarefas = TaskTemplate.query.filter_by(model_id=modelo.id).order_by(TaskTemplate.order).all()
    return jsonify({
        "id": modelo.id,
        "name": modelo.name,
        "tasks": [{"id": t.id, "name": t.name} for t in tarefas]
    })

@views_bp.route("/process/models/update/<int:modelo_id>", methods=["POST"])
@login_required
@admin_required
def atualizar_modelo(modelo_id):
    data = request.get_json()
    modelo = ProcessModel.query.get_or_404(modelo_id)

    try:
        modelo.name = data.get("name", modelo.name)
        TaskTemplate.query.filter_by(model_id=modelo.id).delete()

        for i, t in enumerate(data.get("tasks", []), start=1):
            nova = TaskTemplate(name=t["name"], order=i, model_id=modelo.id)
            db.session.add(nova)

        db.session.commit()
        return jsonify({"message": "Modelo atualizado com sucesso."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar modelo: {str(e)}"}), 500

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

@views_bp.route("/process/models/list")
@login_required
@admin_required
def listar_modelos_json():
    modelos = ProcessModel.query.order_by(ProcessModel.name).all()
    return jsonify([{"id": m.id, "name": m.name} for m in modelos])

# ------------------------- EXCLUSÃO DE PROCESSO INICIADO -------------------------
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

# ------------------------- NOTIFICAÇÕES DE TAREFAS VENCIDAS -------------------------
@views_bp.route("/tarefas-vencidas")
@login_required
def tarefas_vencidas():
    hoje = datetime.utcnow()
    query = Task.query.filter(
        Task.status != "Concluída",
        Task.end_date < hoje
    )

    if not current_user.is_admin:
        query = query.filter(Task.assigned_user_id == current_user.id)

    tarefas = query.all()
    return jsonify({"vencidas": [t.id for t in tarefas]})


# ------------------------- FUNÇÃO DE ENVIO DE NOTIFICAÇÃO POR EMAIL -------------------------
def enviar_email_tarefa_vencida(destinatario, nome_usuario, nome_tarefa, data_vencimento):
    msg = Message(
        subject="Tarefa Vencida",
        sender="seuemail@gmail.com",  # troque pelo seu
        recipients=[destinatario]
    )
    msg.body = (
        f"Olá, {nome_usuario}!\n\n"
        f"A tarefa '{nome_tarefa}' venceu no dia {data_vencimento.strftime('%d/%m/%Y')}.\n"
        "Acesse o sistema para atualizá-la ou concluí-la o quanto antes.\n\n"
        "Atenciosamente,\nSistema de Gerenciamento de Tarefas"
    )
    mail.send(msg)


# ------------------------- VERIFICAÇÃO E NOTIFICAÇÃO DE TAREFAS VENCIDAS -------------------------
@views_bp.route("/notificar-tarefas")
@admin_required
def notificar_tarefas_vencidas():
    hoje = datetime.utcnow()
    tarefas_vencidas = Task.query.filter(
        Task.status != "Concluída",
        Task.end_date < hoje
    ).all()

    for tarefa in tarefas_vencidas:
        usuario = User.query.get(tarefa.assigned_user_id)
        if not usuario or usuario.is_admin:
            continue

        enviar_email_tarefa_vencida(
            destinatario=usuario.email,
            nome_usuario=usuario.name,
            nome_tarefa=tarefa.name,
            data_vencimento=tarefa.end_date
        )

    flash("Notificações de tarefas vencidas enviadas com sucesso.", "success")
    return redirect(url_for("views.kanban"))