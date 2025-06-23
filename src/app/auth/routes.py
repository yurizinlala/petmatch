# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request
# Corrigido: Usar a biblioteca padrão urllib.parse para analisar URLs
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user
# Importar o blueprint 'bp' do __init__.py do módulo auth
from src.app.auth import bp
# Importar formulários e modelos
from src.app.auth.forms import LoginForm, RegistrationForm
from src.app import db # Importar db de src.app
from src.app.models import User # Importar User de src.app.models

# Rota de Login
@bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Email ou senha inválidos.")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        # Redireciona para a página que o usuário tentava acessar, ou para a home
        next_page = request.args.get("next")
        # Verifica se next_page existe e se é um URL relativo (segurança contra Open Redirect)
        # Usando urllib.parse.urlparse
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("main.index")
        flash(f"Bem-vindo(a) de volta, {user.nome_completo}!")
        return redirect(next_page)
    return render_template("auth/login.html", title="Entrar", form=form)

# Rota de Logout
@bp.route("/logout", endpoint="logout")
def logout():
    logout_user()
    flash("Você saiu da sua conta.")
    return redirect(url_for("main.index"))

# Rota de Registro
@bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, # Corrigido: usando o campo username do formulário
                    nome_completo=form.nome_completo.data, # Corrigido: nome_completo em vez de nome
                    email=form.email.data.lower(),
                    telefone=form.telefone.data,
                    endereco=form.endereco.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Parabéns, seu registro foi concluído com sucesso! Faça o login para continuar.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Registrar", form=form)
