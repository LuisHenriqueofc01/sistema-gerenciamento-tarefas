from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import ProcessModel, TaskTemplate, ProcessInstance, Task, User
from datetime import datetime
from sqlalchemy import func
from app.utils.algoritmos import ListaEncadeadaSimples, busca_linear, bubble_sort

process_bp = Blueprint("process", __name__, url_prefix="/process")

# Criar Modelo
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

# Iniciar Processo
@process_bp.route("/start", methods=["POST"])
@login_required
def start_process():
    data = request.json
    model = ProcessModel.query.get(data["model_id"])
    if not model:
        return jsonify({"error": "Modelo não encontrado"}), 404

    instance = ProcessInstance(
        name=data.get("name", model.name),
        model_id=model.id,
        responsavel_id=data.get("responsavel_id")
    )
    db.session.add(instance)
    db.session.commit()

    for template in sorted(model.task_templates, key=lambda x: x.order):
        task = Task(
            title=template.name,
            order=template.order,
            process=instance,
            status="pendente"
        )
        db.session.add(task)

    db.session.commit()
    return jsonify({"message": "Processo iniciado", "process_id": instance.id})

# Listar Tarefas do Processo
@process_bp.route("/<int:process_id>/tasks", methods=["GET"])
@login_required
def list_tasks(process_id):
    tasks = Task.query.filter_by(process_id=process_id).order_by(Task.order).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "order": t.order,
        "assignee": t.assigned_user_id
    } for t in tasks])

# Atualizar status da tarefa
@process_bp.route("/task/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    data = request.json
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    if task.assigned_user_id != current_user.id:
        return jsonify({"error": "Você não tem permissão para alterar esta tarefa"}), 403

    task.status = data.get("status", task.status)

    if task.status == "concluída":
        task.end_date = datetime.utcnow()
        next_task = Task.query.filter_by(
            process_id=task.process_id,
            order=task.order + 1
        ).first()
        if next_task and next_task.status == "pendente":
            next_task.status = "em_progresso"

    db.session.commit()
    return jsonify({"message": "Status da tarefa atualizado com sucesso"})

# Finalizar Processo
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

# Atribuir tarefa
@process_bp.route("/task/<int:task_id>/atribuir", methods=["POST"])
@login_required
def atribuir_usuario(task_id):
    data = request.json
    user_id = data.get("user_id")
    task = Task.query.get(task_id)
    user = User.query.get(user_id)

    if not task:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    task.assigned_user_id = user_id
    db.session.commit()

    return jsonify({"message": f"Tarefa atribuída a {user.name or user.username}"})

# Minhas tarefas
@process_bp.route("/minhas-tarefas", methods=["GET"])
@login_required
def minhas_tarefas():
    status_filtro = request.args.get("status")
    query = Task.query.filter_by(assigned_user_id=current_user.id)
    if status_filtro:
        query = query.filter_by(status=status_filtro)

    tarefas = query.order_by(Task.status, Task.order).all()

    return jsonify([{
        "id": t.id,
        "name": t.title,
        "status": t.status,
        "order": t.order,
        "process_id": t.process_id
    } for t in tarefas])

# Resumo de tarefas por status
@process_bp.route("/minhas-tarefas/resumo", methods=["GET"])
@login_required
def resumo_tarefas():
    resultado = (
        db.session.query(Task.status, func.count(Task.id))
        .filter(Task.assigned_user_id == current_user.id)
        .group_by(Task.status)
        .all()
    )

    contagem = {status: total for status, total in resultado}
    for status_padrao in ["pendente", "em_progresso", "concluída", "validada"]:
        contagem.setdefault(status_padrao, 0)

    return jsonify(contagem)

# Algoritmos (Bubble Sort, Busca Linear, Lista Encadeada)
@process_bp.route("/<int:process_id>/algoritmos", methods=["GET"])
@login_required
def demonstrar_algoritmos(process_id):
    tarefas = Task.query.filter_by(process_id=process_id).all()
    if not tarefas:
        return jsonify({"error": "Nenhuma tarefa encontrada para esse processo"}), 404

    lista = ListaEncadeadaSimples()
    for t in tarefas:
        lista.inserir(t)
    encadeada = [t.title for t in lista.listar()]

    ordenadas = bubble_sort(tarefas[:], chave=lambda x: x.title)
    ordenadas_nome = [t.title for t in ordenadas]

    buscada = busca_linear(tarefas, tarefas[0].title)
    encontrada = buscada.title if buscada else "Não encontrada"

    return jsonify({
        "lista_encadeada": encadeada,
        "ordenadas_por_nome": ordenadas_nome,
        "busca_linear_por_nome": encontrada
    })

# Listar modelos de processo
@process_bp.route("/models/list", methods=["GET"])
@login_required
def listar_modelos():
    modelos = ProcessModel.query.all()
    return jsonify([{"id": m.id, "name": m.name} for m in modelos])

# ✅ NOVA ROTA: Listar usuários (para selecionar o responsável)
@process_bp.route("/users/list", methods=["GET"])
@login_required
def listar_usuarios():
    usuarios = User.query.all()
    return jsonify([{"id": u.id, "name": u.name or u.username} for u in usuarios])
