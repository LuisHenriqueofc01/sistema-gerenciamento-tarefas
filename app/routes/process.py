from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models.models import db, ProcessModel, TaskTemplate, ProcessInstance, Task

process_bp = Blueprint("process", __name__, url_prefix="/process")

@process_bp.route("/models", methods=["POST"])
@login_required
def create_model():
    data = request.json
    model = ProcessModel(name=data["name"])
    db.session.add(model)
    db.session.commit()

    for i, task in enumerate(data.get("tasks", [])):
        task_template = TaskTemplate(name=task["name"], order=i, model=model)
        db.session.add(task_template)

    db.session.commit()
    return jsonify({"message": "Modelo criado com sucesso", "model_id": model.id})

@process_bp.route("/start", methods=["POST"])
@login_required
def start_process():
    data = request.json
    model = ProcessModel.query.get(data["model_id"])
    if not model:
        return jsonify({"error": "Modelo não encontrado"}), 404

    instance = ProcessInstance(name=data.get("name", model.name), model_id=model.id)
    db.session.add(instance)
    db.session.commit()

    for template in sorted(model.task_templates, key=lambda x: x.order):
        task = Task(
            name=template.name,
            order=template.order,
            process=instance,
            status="pendente"
        )
        db.session.add(task)

    db.session.commit()
    return jsonify({"message": "Processo iniciado", "process_id": instance.id})

@process_bp.route("/<int:process_id>/tasks", methods=["GET"])
@login_required
def list_tasks(process_id):
    tasks = Task.query.filter_by(process_id=process_id).order_by(Task.order).all()
    return jsonify([{
        "id": t.id,
        "name": t.name,
        "status": t.status,
        "order": t.order,
        "assignee": t.assignee.name if t.assignee else None
    } for t in tasks])

@process_bp.route("/task/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    data = request.json
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    # 🛡️ Verificação de segurança
    if task.assigned_user_id != current_user.id:
        return jsonify({"error": "Você não tem permissão para alterar esta tarefa"}), 403

    task.status = data.get("status", task.status)

    if task.status == "concluída":
        from datetime import datetime
        task.end_date = datetime.utcnow()

        # Desbloquear próxima tarefa
        next_task = Task.query.filter_by(
            process_id=task.process_id,
            order=task.order + 1
        ).first()

        if next_task and next_task.status == "pendente":
            next_task.status = "em_progresso"

    db.session.commit()
    return jsonify({"message": "Status da tarefa atualizado com sucesso"})



from datetime import datetime

@process_bp.route("/<int:process_id>/finalizar", methods=["POST"])
@login_required
def finalizar_processo(process_id):
    processo = ProcessInstance.query.get(process_id)
    if not processo:
        return jsonify({"error": "Processo não encontrado"}), 404

    tarefas = Task.query.filter_by(process_id=process_id).all()
    todas_concluidas = all(t.status in ["concluída", "validada"] for t in tarefas)

    if not todas_concluidas:
        return jsonify({"error": "Nem todas as tarefas estão concluídas"}), 400

    processo.is_active = False
    processo.end_date = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Processo finalizado com sucesso"})

@process_bp.route("/task/<int:task_id>/atribuir", methods=["POST"])
@login_required
def atribuir_usuario(task_id):
    data = request.json
    user_id = data.get("user_id")

    from app.models.models import User
    task = Task.query.get(task_id)
    user = User.query.get(user_id)

    if not task:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    task.assigned_user_id = user_id
    db.session.commit()

    return jsonify({"message": f"Tarefa atribuída a {user.name}"})

from flask_login import current_user

@process_bp.route("/minhas-tarefas", methods=["GET"])
@login_required
def minhas_tarefas():
    status_filtro = request.args.get("status")  # Ex: em_progresso, pendente, etc.

    query = Task.query.filter_by(assigned_user_id=current_user.id)
    
    if status_filtro:
        query = query.filter_by(status=status_filtro)

    tarefas = query.order_by(Task.status, Task.order).all()

    return jsonify([{
        "id": t.id,
        "name": t.name,
        "status": t.status,
        "order": t.order,
        "process_id": t.process_id
    } for t in tarefas])

@process_bp.route("/minhas-tarefas/resumo", methods=["GET"])
@login_required
def resumo_tarefas():
    from sqlalchemy import func
    resultado = (
        db.session.query(Task.status, func.count(Task.id))
        .filter(Task.assigned_user_id == current_user.id)
        .group_by(Task.status)
        .all()
    )

    contagem = {status: total for status, total in resultado}

    # Garante que todos os status apareçam, mesmo que zerados
    for status_padrao in ["pendente", "em_progresso", "concluída", "validada"]:
        contagem.setdefault(status_padrao, 0)

    return jsonify(contagem)
