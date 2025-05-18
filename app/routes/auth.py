from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# --------------------- REGISTRO VIA JSON (API opcional) ---------------------
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


# --------------------- LOGIN VIA FORMULÁRIO ---------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login bem-sucedido!", "success")
            return redirect(url_for("views.admin_panel" if user.is_admin else "views.kanban"))
        else:
            flash("Credenciais inválidas", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# --------------------- API para saber quem está logado ---------------------
@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "username": current_user.username,
        "name": current_user.name,
        "is_admin": current_user.is_admin
    })


# --------------------- LOGOUT ---------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
