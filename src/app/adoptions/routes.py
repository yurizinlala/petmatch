# -*- coding: utf-8 -*-
from flask import redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
from src.app.adoptions import bp
from src.app import db
from src.app.models import Pet, Adoption, User

# Rota para solicitar adoção (requer login)
@bp.route("/pedir/<int:pet_id>", methods=["POST"], endpoint="request_adoption")
@login_required
def request_adoption(pet_id):
    pet = Pet.query.get_or_404(pet_id)

    # Verificar se o pet está disponível
    if pet.status != "Disponível":
        flash("Este pet não está mais disponível para adoção.")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

    # Verificar se o usuário já tem um pedido pendente para este pet
    existing_request = Adoption.query.filter_by(id_adotante=current_user.id, id_pet=pet.id, status="Pendente").first()
    if existing_request:
        flash("Você já tem um pedido de adoção pendente para este pet.")
        return redirect(url_for("adoptions.request_history"))

    # Criar o registro de adoção
    try:
        adoption = Adoption(id_pet=pet.id, id_adotante=current_user.id, status="Pendente")
        pet.status = "Em Adoção" # Atualiza status do pet
        db.session.add(adoption)
        db.session.add(pet) # Adiciona o pet para salvar a mudança de status
        db.session.commit()
        flash("Seu pedido de adoção foi enviado com sucesso! Acompanhe o status em \'Meus Pedidos\'.")
        # Redirecionar para o histórico de pedidos do usuário
        return redirect(url_for("adoptions.request_history"))
    except Exception as e:
        db.session.rollback()
        flash(f"Ocorreu um erro ao processar seu pedido: {e}")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))

# Rota para visualizar histórico de pedidos (requer login)
@bp.route("/meus_pedidos", endpoint="request_history")
@login_required
def request_history():
    # Buscar todos os pedidos do usuário atual, ordenados por data
    adoptions = Adoption.query.filter_by(id_adotante=current_user.id).order_by(Adoption.data_pedido.desc()).all()
    return render_template("adoptions/request_history.html", title="Meus Pedidos de Adoção", adoptions=adoptions)

# Rota para cancelar um pedido PENDENTE (pelo próprio adotante)
@bp.route("/cancelar_pedido/<int:adoption_id>", methods=["POST"], endpoint="cancel_my_request")
@login_required
def cancel_my_request(adoption_id):
    adoption = Adoption.query.get_or_404(adoption_id)

    # Verificar se o pedido pertence ao usuário logado e se está pendente
    if adoption.id_adotante != current_user.id:
        abort(403) # Não autorizado
    if adoption.status != "Pendente":
        flash("Este pedido não pode mais ser cancelado por você.")
        return redirect(url_for("adoptions.request_history"))

    pet = Pet.query.get(adoption.id_pet)
    try:
        adoption.status = "Cancelada"
        if pet and pet.status == "Em Adoção": # Só volta para disponível se estava "Em Adoção"
            pet.status = "Disponível"
            db.session.add(pet)

        db.session.add(adoption)
        db.session.commit()
        flash("Seu pedido de adoção foi cancelado.")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao cancelar o pedido: {e}")

    return redirect(url_for("adoptions.request_history"))

