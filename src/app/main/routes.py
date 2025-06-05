# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
# Corrigir o import para usar o caminho completo a partir da raiz do projeto (src)
from src.app.main import bp
from src.app.models import Adocao, Pet

@bp.route("/")
@bp.route("/index")
def index():
    # Futuramente, pode buscar pets em destaque ou informações do dashboard
    # Certifique-se que o template exista em src/app/templates/main/index.html
    return render_template("main/index.html", title="Bem-vindo")

# Dashboard do usuário (requer login)
@bp.route("/dashboard")
@login_required
def dashboard():
    # Buscar adoções do usuário
    adocoes = Adocao.query.filter_by(adotante_id=current_user.id).order_by(Adocao.data_pedido.desc()).all()
    
    # Separar adoções por status para melhor visualização
    adocoes_pendentes = [a for a in adocoes if a.status == "pendente"]
    adocoes_aprovadas = [a for a in adocoes if a.status == "aprovada"]
    adocoes_rejeitadas = [a for a in adocoes if a.status == "rejeitada"]
    
    return render_template(
        "main/dashboard.html", 
        title="Meu Painel", 
        adocoes_pendentes=adocoes_pendentes,
        adocoes_aprovadas=adocoes_aprovadas,
        adocoes_rejeitadas=adocoes_rejeitadas,
        total_adocoes=len(adocoes)
    )
