from app import create_app, db
from app.models.models import Task
from datetime import datetime

app = create_app()
with app.app_context():
    tarefas = Task.query.filter(Task.status != "Concluída", Task.end_date < datetime.utcnow()).all()
    if not tarefas:
        print("Nenhuma tarefa vencida encontrada.")
    for t in tarefas:
        print(f"[TAREFA] {t.title} | Vencimento: {t.end_date} | Status: {t.status} | Usuário ID: {t.assigned_user_id}")
