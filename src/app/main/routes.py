# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional
# Corrigir o import para usar o caminho completo a partir da raiz do projeto (src)
from src.app.main import bp
from src.app.models import Adocao, Pet, User
from src.app import db

# Formulário para edição de perfil
class ProfileForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(message="Nome completo é obrigatório")])
    email = StringField('Email', validators=[DataRequired(message="Email é obrigatório"), Email(message="Email inválido")])
    telefone = TelField('Telefone', validators=[Optional(), Length(min=10, max=15, message="Telefone deve ter entre 10 e 15 caracteres")])
    endereco = TextAreaField('Endereço', validators=[Optional(), Length(max=200, message="Endereço deve ter no máximo 200 caracteres")])
    perfil_adotante = TextAreaField('Perfil de Adotante', validators=[Optional(), Length(max=500, message="Perfil deve ter no máximo 500 caracteres")])

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
    # Se for admin, redirecionar para o dashboard administrativo
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Buscar adoções do usuário
    adocoes = Adocao.query.filter_by(adotante_id=current_user.id).order_by(Adocao.data_pedido.desc()).all()
    
    # Separar adoções por status para melhor visualização
    adocoes_pendentes = [a for a in adocoes if a.status == "pendente"]
    adocoes_aprovadas = [a for a in adocoes if a.status == "aprovada"]
    adocoes_rejeitadas = [a for a in adocoes if a.status == "rejeitada"]
    adocoes_canceladas = [a for a in adocoes if a.status == "cancelada"]
    
    return render_template(
        "main/dashboard.html", 
        title="Meu Painel", 
        adocoes_pendentes=adocoes_pendentes,
        adocoes_aprovadas=adocoes_aprovadas,
        adocoes_rejeitadas=adocoes_rejeitadas,
        adocoes_canceladas=adocoes_canceladas,
        total_adocoes=len(adocoes)
    )

# Edição de perfil do usuário
@bp.route("/editar-perfil", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileForm()
    
    # Preencher o formulário com os dados atuais do usuário no GET
    if request.method == "GET":
        form.nome_completo.data = current_user.nome_completo
        form.email.data = current_user.email
        form.telefone.data = current_user.telefone
        form.endereco.data = current_user.endereco
        form.perfil_adotante.data = current_user.perfil_adotante
    
    # Processar o formulário no POST
    if form.validate_on_submit():
        # Verificar se o email já está em uso por outro usuário
        if form.email.data != current_user.email:
            user_with_email = User.query.filter_by(email=form.email.data).first()
            if user_with_email and user_with_email.id != current_user.id:
                flash("Este email já está sendo usado por outro usuário.", "danger")
                return render_template("main/edit_profile.html", title="Editar Perfil", form=form)
        
        # Atualizar os dados do usuário
        current_user.nome_completo = form.nome_completo.data
        current_user.email = form.email.data
        current_user.telefone = form.telefone.data
        current_user.endereco = form.endereco.data
        current_user.perfil_adotante = form.perfil_adotante.data
        
        try:
            db.session.commit()
            flash("Seu perfil foi atualizado com sucesso!", "success")
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar perfil: {e}", "danger")
    
    # Se houver erros de validação, exibir mensagens
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")
    
    return render_template("main/edit_profile.html", title="Editar Perfil", form=form)
