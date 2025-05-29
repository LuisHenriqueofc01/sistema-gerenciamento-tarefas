from app import create_app, db, mail
from app.models.models import Task, User
from flask_mail import Message
from datetime import datetime, timezone
from flask import render_template_string

app = create_app()

with app.app_context():
    # Busca todas as tarefas vencidas que ainda não foram concluídas
    tarefas = Task.query.filter(
        Task.status != "Concluída",
        Task.end_date < datetime.now(timezone.utc)
    ).all()

    # Agrupar tarefas por usuário
    tarefas_por_usuario = {}
    for t in tarefas:
        if t.assigned_user_id not in tarefas_por_usuario:
            tarefas_por_usuario[t.assigned_user_id] = []
        tarefas_por_usuario[t.assigned_user_id].append(t)

    # Enviar um e-mail por usuário
    for user_id, tarefas_user in tarefas_por_usuario.items():
        usuario = db.session.get(User, user_id)
        if not usuario or not usuario.email:
            continue

        corpo_html = render_template_string("""
        <h3>Olá {{ nome }},</h3>
        <p>Você possui as seguintes tarefas vencidas:</p>
        <ul>
        {% for t in tarefas %}
            <li><strong>{{ t.title }}</strong> - vencida em {{ t.end_date.strftime('%d/%m/%Y') }}</li>
        {% endfor %}
        </ul>
        <p>Acesse o sistema para atualizá-las.</p>
        """, nome=usuario.name, tarefas=tarefas_user)

        msg = Message(subject="Tarefas Vencidas",
                      recipients=[usuario.email],
                      html=corpo_html)

        try:
            mail.send(msg)
            print(f"E-mail enviado para: {usuario.email}")
        except Exception as e:
            print(f"Erro ao enviar e-mail para {usuario.email}: {e}")
