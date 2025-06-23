# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from src.app.pets import bp
from src.app import db
from src.app.models import Pet
from src.app.pets.forms import PetForm, ESPECIE_CHOICES, PORTE_CHOICES, SEXO_CHOICES

# Decorator para verificar se o usuário é admin
from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Listagem de Pets (Acessível a todos) - COM FILTROS
@bp.route("/", methods=["GET"], endpoint="list_pets")
def list_pets():
    # Obter parâmetros de filtro da query string
    especie_filter = request.args.get("especie", default=None, type=str)
    porte_filter = request.args.get("porte", default=None, type=str)
    sexo_filter = request.args.get("sexo", default=None, type=str)
    idade_min_filter = request.args.get("idade_min", default=None, type=int)
    idade_max_filter = request.args.get("idade_max", default=None, type=int)

    # Construir a query base
    query = Pet.query.filter(Pet.status != "adotado")

    # Aplicar filtros
    if especie_filter:
        query = query.filter(Pet.especie == especie_filter)
    if porte_filter:
        query = query.filter(Pet.porte == porte_filter)
    if sexo_filter:
        query = query.filter(Pet.sexo == sexo_filter)
    if idade_min_filter is not None:
        query = query.filter(Pet.idade >= idade_min_filter)
    if idade_max_filter is not None:
        query = query.filter(Pet.idade <= idade_max_filter)

    # Ordenar e executar a query
    pets = query.order_by(Pet.data_cadastro.desc()).all()

    # Passar filtros atuais para o template poder preencher o formulário
    current_filters = {
        "especie": especie_filter,
        "porte": porte_filter,
        "sexo": sexo_filter,
        "idade_min": idade_min_filter,
        "idade_max": idade_max_filter
    }

    return render_template("pets/list_pets.html",
                           title="Pets para Adoção",
                           pets=pets,
                           especie_choices=ESPECIE_CHOICES,
                           porte_choices=PORTE_CHOICES,
                           sexo_choices=SEXO_CHOICES,
                           current_filters=current_filters)

# Detalhes do Pet (Acessível a todos)
@bp.route("/<int:pet_id>", endpoint="pet_details")
def pet_details(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template("pets/pet_details.html", title=pet.nome, pet=pet)

# Adicionar Novo Pet (Admin)
@bp.route("/novo", methods=["GET", "POST"], endpoint="add_pet")
@login_required
@admin_required
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        pet = Pet(nome=form.nome.data,
                  especie=form.especie.data,
                  raca=form.raca.data,
                  idade=form.idade.data,
                  porte=form.porte.data,
                  sexo=form.sexo.data,
                  descricao=form.descricao.data,
                  foto=form.foto.data if form.foto.data else None,
                  status="disponível") # Status inicial padronizado
        db.session.add(pet)
        db.session.commit()
        flash(f"Pet {pet.nome} cadastrado com sucesso!")
        return redirect(url_for("pets.list_pets"))
    return render_template("pets/pet_form.html", title="Adicionar Novo Pet", form=form, legend="Adicionar Novo Pet")

# Editar Pet (Admin)
@bp.route("/<int:pet_id>/editar", methods=["GET", "POST"], endpoint="edit_pet")
@login_required
@admin_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = PetForm(obj=pet) # Preenche o formulário com dados do pet
    if form.validate_on_submit():
        pet.nome = form.nome.data
        pet.especie = form.especie.data
        pet.raca = form.raca.data
        pet.idade = form.idade.data
        pet.porte = form.porte.data
        pet.sexo = form.sexo.data
        pet.descricao = form.descricao.data
        pet.foto = form.foto.data if form.foto.data else pet.foto # Mantém a URL antiga se o campo vier vazio
        # pet.status = form.status.data # Se o status fosse editável no form
        db.session.commit()
        flash(f"Dados do pet {pet.nome} atualizados com sucesso!")
        return redirect(url_for("pets.pet_details", pet_id=pet.id))
    return render_template("pets/pet_form.html", title="Editar Pet", form=form, legend=f"Editar Pet: {pet.nome}", pet=pet)

# Deletar Pet (Admin)
@bp.route("/<int:pet_id>/deletar", methods=["POST"], endpoint="delete_pet")
@login_required
@admin_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    # Adicionar verificação se o pet tem adoção pendente/confirmada antes de deletar?
    if pet.adocoes.count() > 0 and any(adocao.status != "rejeitada" for adocao in pet.adocoes):
        flash("Não é possível remover um pet com um processo de adoção ativo ou confirmado.", "danger")
        return redirect(url_for("pets.list_pets"))
    try:
        db.session.delete(pet)
        db.session.commit()
        flash(f"Pet {pet.nome} removido com sucesso.", "success")
        return redirect(url_for("pets.list_pets"))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao remover o pet: {e}", "danger")
        return redirect(url_for("pets.list_pets"))
