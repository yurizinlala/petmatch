# -*- coding: utf-8 -*-
from flask import render_template
# Corrigir o import para usar o caminho completo a partir da raiz do projeto (src)
from src.app.main import bp

@bp.route("/")
@bp.route("/index")
def index():
    # Futuramente, pode buscar pets em destaque ou informações do dashboard
    # Certifique-se que o template exista em src/app/templates/main/index.html
    return render_template("main/index.html", title="Bem-vindo")

# Outras rotas do main blueprint (ex: dashboard do adotante) virão aqui
@bp.route("/dashboard")
# @login_required # Adicionar depois que o login estiver funcional
def dashboard():
    # Lógica do dashboard do adotante
    # Certifique-se que o template exista em src/app/templates/main/dashboard.html
    # return render_template("main/dashboard.html", title="Meu Painel")
    # Por enquanto, vamos retornar algo simples para testar
    # Criar o arquivo src/app/templates/main/dashboard.html se não existir
    # return "<h1>Painel do Adotante (Dashboard)</h1>"
    # Temporariamente redirecionar para a home para evitar erro se dashboard.html não existir
    from flask import redirect, url_for
    return redirect(url_for('main.index'))

