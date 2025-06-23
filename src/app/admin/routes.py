# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, abort, Response, request
from flask_login import login_required, current_user
from src.app.admin import bp
from src.app import db
from src.app.models import Adocao, Pet, User
from src.app.pets.forms import ESPECIE_CHOICES
from functools import wraps
from sqlalchemy import func, extract
import csv
from io import StringIO
from datetime import datetime, timedelta

# Decorator para verificar se o usuário é admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Rota principal do painel admin - SUBSTITUÍDA PELO DASHBOARD EXCLUSIVO
@bp.route("/", endpoint="dashboard")
@login_required
@admin_required
def dashboard():
    # Contadores para o dashboard
    pets_disponiveis = Pet.query.filter_by(status="disponível").count()
    pets_em_processo = Pet.query.filter_by(status="em processo").count()
    pets_adotados = Pet.query.filter_by(status="adotado").count()
    
    # Adoções pendentes para exibição direta no dashboard
    adocoes_pendentes = Adocao.query.filter_by(status="pendente").order_by(Adocao.data_pedido.asc()).all()
    adocoes_pendentes_count = len(adocoes_pendentes)
    
    # Estatísticas adicionais
    total_usuarios = User.query.filter_by(is_admin=False).count()
    
    # Adoções recentes (últimos 7 dias)
    data_limite = datetime.utcnow() - timedelta(days=7)
    adocoes_recentes = Adocao.query.filter(
        Adocao.data_pedido >= data_limite
    ).order_by(Adocao.data_pedido.desc()).limit(5).all()
    
    return render_template(
        "admin/dashboard.html", 
        title="Painel Administrativo",
        pets_disponiveis=pets_disponiveis,
        pets_em_processo=pets_em_processo,
        pets_adotados=pets_adotados,
        adocoes_pendentes=adocoes_pendentes,
        adocoes_pendentes_count=adocoes_pendentes_count,
        total_usuarios=total_usuarios,
        adocoes_recentes=adocoes_recentes
    )

# Rota para gerenciar pets
@bp.route("/pets", endpoint="manage_pets")
@login_required
@admin_required
def manage_pets():
    # Obter parâmetros de filtro
    status_filter = request.args.get("status", default=None, type=str)
    especie_filter = request.args.get("especie", default=None, type=str)
    
    # Construir a query base
    query = Pet.query
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Pet.status == status_filter)
    if especie_filter:
        query = query.filter(Pet.especie == especie_filter)
    
    # Ordenar e executar a query
    pets = query.order_by(Pet.data_cadastro.desc()).all()
    
    # Passar filtros atuais para o template
    current_filters = {
        "status": status_filter,
        "especie": especie_filter
    }
    
    return render_template(
        "admin/manage_pets.html",
        title="Gerenciamento de Pets",
        pets=pets,
        especie_choices=ESPECIE_CHOICES,
        current_filters=current_filters
    )

# Rota para listar pedidos de adoção pendentes
@bp.route("/adocoes/pendentes", endpoint="pending_adoptions")
@login_required
@admin_required
def pending_adoptions():
    adocoes_pendentes = Adocao.query.filter_by(status="pendente").order_by(Adocao.data_pedido.asc()).all()
    return render_template(
        "admin/pending_adoptions.html", 
        title="Pedidos de Adoção Pendentes", 
        adoptions=adocoes_pendentes
    )

# Rota para APROVAR um pedido de adoção
@bp.route("/adocoes/<int:adocao_id>/aprovar", methods=["POST"], endpoint="approve_adoption")
@login_required
@admin_required
def approve_adoption(adocao_id):
    adocao = Adocao.query.get_or_404(adocao_id)
    
    if adocao.status != "pendente":
        flash("Este pedido já foi processado.", "warning")
        return redirect(url_for("admin.dashboard"))
    
    pet = Pet.query.get(adocao.pet_id)
    if not pet:
        flash("Erro: Pet associado a este pedido não encontrado.", "danger")
        adocao.status = "rejeitada"
        db.session.add(adocao)
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    
    try:
        # Atualizar status da adoção
        adocao.status = "aprovada"
        adocao.data_decisao = datetime.utcnow()
        
        # Atualizar status do pet
        pet.status = "adotado"
        
        # Rejeitar outros pedidos pendentes para o mesmo pet
        outros_pedidos = Adocao.query.filter(
            Adocao.pet_id == pet.id,
            Adocao.status == "pendente",
            Adocao.id != adocao.id
        ).all()
        
        for outro_pedido in outros_pedidos:
            outro_pedido.status = "rejeitada"
            outro_pedido.data_decisao = datetime.utcnow()
            db.session.add(outro_pedido)
        
        db.session.add(adocao)
        db.session.add(pet)
        db.session.commit()
        
        flash(f"Adoção do pet {pet.nome} aprovada com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao aprovar a adoção: {e}", "danger")
    
    # Redirecionar para o dashboard admin em vez da página de pendentes
    return redirect(url_for("admin.dashboard"))

# Rota para REJEITAR um pedido de adoção
@bp.route("/adocoes/<int:adocao_id>/rejeitar", methods=["POST"], endpoint="reject_adoption")
@login_required
@admin_required
def reject_adoption(adocao_id):
    adocao = Adocao.query.get_or_404(adocao_id)
    
    if adocao.status != "pendente":
        flash("Este pedido já foi processado.", "warning")
        return redirect(url_for("admin.dashboard"))
    
    pet = Pet.query.get(adocao.pet_id)
    
    try:
        # Atualizar status da adoção
        adocao.status = "rejeitada"
        adocao.data_decisao = datetime.utcnow()
        
        # Verificar se não há outros pedidos pendentes para este pet
        outro_pedido_pendente = Adocao.query.filter(
            Adocao.pet_id == adocao.pet_id,
            Adocao.status == "pendente",
            Adocao.id != adocao.id
        ).first()
        
        # Se não houver outros pedidos pendentes, voltar o pet para disponível
        if pet and not outro_pedido_pendente:
            pet.status = "disponível"
            db.session.add(pet)
        
        db.session.add(adocao)
        db.session.commit()
        
        flash(f"Pedido de adoção para o pet {pet.nome if pet else 'desconhecido'} foi rejeitado.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao rejeitar a adoção: {e}", "danger")
    
    # Redirecionar para o dashboard admin em vez da página de pendentes
    return redirect(url_for("admin.dashboard"))

# Rota para histórico de adoções
@bp.route("/adocoes/historico", endpoint="adoption_history")
@login_required
@admin_required
def adoption_history():
    # Obter parâmetros de filtro
    status_filter = request.args.get("status", default=None, type=str)
    
    # Construir a query base
    query = Adocao.query
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Adocao.status == status_filter)
    
    # Ordenar e executar a query
    adocoes = query.order_by(Adocao.data_pedido.desc()).all()
    
    return render_template(
        "admin/adoption_history.html",
        title="Histórico de Adoções",
        adocoes=adocoes,
        status_filter=status_filter
    )


# Rota para gerenciar todos os processos de adoção
@bp.route("/adocoes/gerenciar", endpoint="manage_adoptions")
@login_required
@admin_required
def manage_adoptions():
    # Obter parâmetros de filtro
    status_filter = request.args.get("status", default=None, type=str)
    
    # Construir a query base
    query = Adocao.query
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Adocao.status == status_filter)
    
    # Ordenar e executar a query
    adocoes = query.order_by(Adocao.data_pedido.desc()).all()
    
    return render_template(
        "admin/manage_adoptions.html",
        title="Processo de Adoções",
        adocoes=adocoes,
        status_filter=status_filter
    )


