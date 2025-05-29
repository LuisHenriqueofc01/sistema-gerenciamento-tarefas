import schedule
import threading
import time
from datetime import datetime, timezone
from app import create_app, db, mail
from app.models.models import Task, User
from flask_mail import Message
from flask import render_template_string

def verificar_tarefas():
    app = create_app()
    with app.app_context():
        # Usando datetime.now com timezone.utc para evitar depreciação
        agora = datetime.now(timezone.utc)
        tarefas = Task.query.filter(Task.status != "Concluída", Task.end_date < agora).all()

        tarefas_por_usuario = {}
        for t in tarefas:
            if t.assigned_user_id not in tarefas_por_usuario:
                tarefas_por_usuario[t.assigned_user_id] = []
            tarefas_por_usuario[t.assigned_user_id].append(t)

        for user_id, tarefas_user in tarefas_por_usuario.items():
            usuario = User.query.get(user_id)
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
                print(f"[{datetime.now()}] E-mail enviado para: {usuario.email}")
            except Exception as e:
                print(f"Erro ao enviar e-mail para {usuario.email}: {e}")

def start_scheduler():
    def run_scheduler():
        schedule.every().day.at("08:00").do(verificar_tarefas)
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()
