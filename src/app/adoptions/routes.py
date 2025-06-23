# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from src.app.adoptions import bp
from src.app import db
from src.app.models import Adocao, Pet, User
from datetime import datetime

# Decorator para verificar se o usuário é admin (pode ser movido para um utils)
from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Rota para solicitar adoção (requer login)
@bp.route("/solicitar/<int:pet_id>", methods=["POST"], endpoint="request_adoption")
@login_required
def request_adoption(pet_id):
    pet = Pet.query.get_or_404(pet_id)

    # Verificar se o pet está disponível
    if pet.status != "disponível":
        flash("Este pet não está mais disponível para adoção no momento.", "warning")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

    # Verificar se o usuário já tem um pedido pendente para este pet
    pedido_existente = Adocao.query.filter_by(adotante_id=current_user.id, pet_id=pet.id, status="pendente").first()
    if pedido_existente:
        flash("Você já possui um pedido de adoção pendente para este pet.", "info")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

    # Criar o registro de adoção
    try:
        nova_adocao = Adocao(pet_id=pet.id, adotante_id=current_user.id, status="pendente")
        pet.status = "em processo" # Atualiza status do pet
        db.session.add(nova_adocao)
        db.session.add(pet) # Adiciona a atualização do pet à sessão
        db.session.commit()
        flash("Pedido de adoção enviado com sucesso! Entraremos em contato em breve.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Ocorreu um erro ao processar seu pedido: {e}", "danger")

    return redirect(url_for("pets.pet_details", pet_id=pet.id))

# Rota para o histórico de pedidos do usuário (requer login)
@bp.route("/meus-pedidos", endpoint="request_history")
@login_required
def request_history():
    pedidos = Adocao.query.filter_by(adotante_id=current_user.id).order_by(Adocao.data_pedido.desc()).all()
    return render_template("adoptions/request_history.html", title="Meus Pedidos de Adoção", adoptions=pedidos)

# Rota para cancelar um pedido de adoção pelo próprio usuário (requer login)
@bp.route("/cancelar/<int:adoption_id>", methods=["POST"], endpoint="cancel_my_request")
@login_required
def cancel_my_request(adoption_id):
    adocao = Adocao.query.get_or_404(adoption_id)
    
    # Verificar se o pedido pertence ao usuário logado
    if adocao.adotante_id != current_user.id:
        flash("Você não tem permissão para cancelar este pedido.", "danger")
        return redirect(url_for("adoptions.request_history"))
    
    # Verificar se o pedido ainda está pendente
    if adocao.status != "pendente":
        flash("Apenas pedidos pendentes podem ser cancelados.", "warning")
        return redirect(url_for("adoptions.request_history"))
    
    pet = Pet.query.get(adocao.pet_id)
    
    try:
        # Atualizar status da adoção
        adocao.status = "cancelada"
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
        
        flash(f"Seu pedido de adoção para {pet.nome if pet else 'o pet'} foi cancelado com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao cancelar o pedido: {e}", "danger")
    
    return redirect(url_for("adoptions.request_history"))

# --- Rotas de Administração --- #

# Aprovar Adoção (Admin)
@bp.route("/aprovar/<int:adocao_id>", methods=["POST"], endpoint="approve_adoption")
@login_required
@admin_required
def approve_adoption(adocao_id):
    adocao = Adocao.query.get_or_404(adocao_id)
    pet = Pet.query.get(adocao.pet_id)

    if adocao.status != "pendente":
        flash("Este pedido já foi processado.", "warning")
        return redirect(url_for("admin.pending_adoptions"))

    try:
        adocao.status = "aprovada"
        adocao.data_decisao = datetime.utcnow()
        if pet:
            pet.status = "adotado"
            db.session.add(pet)
        
        # Rejeitar outros pedidos pendentes para o mesmo pet
        outros_pedidos = Adocao.query.filter(
            Adocao.pet_id == adocao.pet_id,
            Adocao.status == "pendente",
            Adocao.id != adocao.id
        ).all()
        for outro_pedido in outros_pedidos:
            outro_pedido.status = "rejeitada"
            outro_pedido.data_decisao = datetime.utcnow()
            db.session.add(outro_pedido)

        db.session.add(adocao)
        db.session.commit()
        flash(f"Adoção do pet {pet.nome if pet else '.'} aprovada com sucesso!", "success")
        # TODO: Enviar email de notificação para o adotante
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao aprovar a adoção: {e}", "danger")

    return redirect(url_for("admin.pending_adoptions"))

# Rejeitar Adoção (Admin)
@bp.route("/rejeitar/<int:adocao_id>", methods=["POST"], endpoint="reject_adoption")
@login_required
@admin_required
def reject_adoption(adocao_id):
    adocao = Adocao.query.get_or_404(adocao_id)
    pet = Pet.query.get(adocao.pet_id)

    if adocao.status != "pendente":
        flash("Este pedido já foi processado.", "warning")
        return redirect(url_for("admin.pending_adoptions"))

    try:
        adocao.status = "rejeitada"
        adocao.data_decisao = datetime.utcnow()
        if pet:
            # Verificar se não há outros pedidos pendentes para este pet antes de voltar para disponível
            outro_pedido_pendente = Adocao.query.filter(
                Adocao.pet_id == adocao.pet_id,
                Adocao.status == "pendente",
                Adocao.id != adocao.id
            ).first()
            if not outro_pedido_pendente:
                 pet.status = "disponível"
                 db.session.add(pet)

        db.session.add(adocao)
        db.session.commit()
        flash(f"Pedido de adoção para o pet {pet.nome if pet else '.'} rejeitado.", "info")
        # TODO: Enviar email de notificação para o adotante
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao rejeitar a adoção: {e}", "danger")

    return redirect(url_for("admin.pending_adoptions"))
