from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User
from flask_login import logout_user
from flask import redirect, url_for

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Usuário já existe"}), 400

    user = User(username=data["username"], name=data["name"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário registrado com sucesso"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and user.check_password(data["password"]):
        login_user(user)
        return jsonify({"message": "Login bem-sucedido", "user_id": user.id})
    return jsonify({"error": "Credenciais inválidas"}), 401


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"username": current_user.username, "name": current_user.name})


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))  # ou outra rota pública, como /login
