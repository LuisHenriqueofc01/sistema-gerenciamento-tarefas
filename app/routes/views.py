from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.models import ProcessInstance

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    return render_template("index.html")

@views_bp.route("/criar-modelo")
def criar_modelo():
    return render_template("criar_modelo.html")

@views_bp.route("/iniciar-processo")
def iniciar_processo():
    return render_template("iniciar_processo.html")

@views_bp.route("/kanban")
@login_required
def kanban():
    return render_template("kanban.html")

@views_bp.route("/revisao-processo")
@login_required
def revisao_processo():
    return render_template("revisao.html")

# Página genérica após finalização
@views_bp.route("/processo-finalizado")
@login_required
def processo_finalizado_pagina():
    return render_template("processo-finalizado.html")

# Página com ID de processo específico
@views_bp.route("/processo-finalizado/<int:process_id>")
@login_required
def processo_finalizado_com_id(process_id):
    processo = ProcessInstance.query.get_or_404(process_id)
    return render_template("processo-finalizado.html", processo=processo, usuario=current_user)
