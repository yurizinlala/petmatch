# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, abort, Response, request
from flask_login import login_required, current_user
from src.app.admin import bp
from src.app import db
from src.app.models import Adoption, Pet, User
from src.app.pets.routes import admin_required # Reutilizar o decorator
from sqlalchemy import func, extract
import csv
from io import StringIO
from datetime import datetime, timedelta

# Rota principal do painel admin (pode mostrar dashboard ou redirecionar)
@bp.route("/", endpoint="dashboard")
@login_required
@admin_required
def dashboard():
    # Por enquanto, redireciona para a lista de pedidos pendentes
    return redirect(url_for("admin.pending_adoptions"))

# Rota para listar pedidos de adoção pendentes
@bp.route("/pedidos_pendentes", endpoint="pending_adoptions")
@login_required
@admin_required
def pending_adoptions():
    pending = Adoption.query.filter_by(status="Pendente").order_by(Adoption.data_pedido.asc()).all()
    return render_template("admin/pending_adoptions.html", title="Pedidos Pendentes", adoptions=pending)

# Rota para APROVAR um pedido de adoção
@bp.route("/pedidos/<int:adoption_id>/aprovar", methods=["POST"], endpoint="approve_adoption")
@login_required
@admin_required
def approve_adoption(adoption_id):
    adoption = Adoption.query.get_or_404(adoption_id)
    if adoption.status != "Pendente":
        flash("Este pedido não está mais pendente.")
        return redirect(url_for("admin.pending_adoptions"))

    pet = Pet.query.get(adoption.id_pet)
    if not pet:
        flash("Erro: Pet associado a este pedido não encontrado.")
        adoption.status = "Cancelada"
        db.session.add(adoption)
        db.session.commit()
        return redirect(url_for("admin.pending_adoptions"))

    try:
        adoption.status = "Confirmada"
        pet.status = "Adotado"
        db.session.add(adoption)
        db.session.add(pet)

        outros_pedidos = Adoption.query.filter(
            Adoption.id_pet == pet.id,
            Adoption.status == "Pendente",
            Adoption.id != adoption.id
        ).all()
        for outro_pedido in outros_pedidos:
            outro_pedido.status = "Cancelada"
            db.session.add(outro_pedido)

        db.session.commit()
        flash(f"Pedido de adoção para {pet.nome} aprovado com sucesso!")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao aprovar o pedido: {e}")

    return redirect(url_for("admin.pending_adoptions"))

# Rota para CANCELAR um pedido de adoção (pelo admin)
@bp.route("/pedidos/<int:adoption_id>/cancelar", methods=["POST"], endpoint="cancel_adoption")
@login_required
@admin_required
def cancel_adoption(adoption_id):
    adoption = Adoption.query.get_or_404(adoption_id)
    if adoption.status != "Pendente":
        flash("Este pedido não está mais pendente.")
        return redirect(url_for("admin.pending_adoptions"))

    pet = Pet.query.get(adoption.id_pet)
    try:
        adoption.status = "Cancelada"
        if pet and pet.status == "Em Adoção":
            pet.status = "Disponível"
            db.session.add(pet)

        db.session.add(adoption)
        db.session.commit()
        flash(f"Pedido de adoção para {pet.nome if pet else \"Pet não encontrado\"} cancelado.")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao cancelar o pedido: {e}")

    return redirect(url_for("admin.pending_adoptions"))

# Rota para Relatórios
@bp.route("/relatorios", methods=["GET"], endpoint="reports")
@login_required
@admin_required
def reports():
    # 1. Total de adoções confirmadas por mês (últimos 12 meses)
    today = datetime.utcnow()
    one_year_ago = today - timedelta(days=365)
    adoptions_by_month = db.session.query(
        extract("year", Adoption.data_atualizacao).label("year"),
        extract("month", Adoption.data_atualizacao).label("month"),
        func.count(Adoption.id).label("count")
    ).filter(
        Adoption.status == "Confirmada",
        Adoption.data_atualizacao >= one_year_ago
    ).group_by(
        extract("year", Adoption.data_atualizacao),
        extract("month", Adoption.data_atualizacao)
    ).order_by(
        extract("year", Adoption.data_atualizacao).desc(),
        extract("month", Adoption.data_atualizacao).desc()
    ).all()

    # Formatar para exibição (ex: "Jan/2024: 5")
    monthly_data = [f"{datetime(int(r.year), int(r.month), 1).strftime("%b/%Y")}: {r.count}" for r in adoptions_by_month]

    # 2. Pets mais adotados (por espécie/raça - simplificado)
    most_adopted_species = db.session.query(
        Pet.especie,
        func.count(Adoption.id).label("count")
    ).join(Adoption, Pet.id == Adoption.id_pet)
    .filter(Adoption.status == "Confirmada")
    .group_by(Pet.especie)
    .order_by(func.count(Adoption.id).desc())
    .limit(5)
    .all()

    most_adopted_breeds = db.session.query(
        Pet.raca,
        Pet.especie,
        func.count(Adoption.id).label("count")
    ).join(Adoption, Pet.id == Adoption.id_pet)
    .filter(Adoption.status == "Confirmada")
    .group_by(Pet.raca, Pet.especie)
    .order_by(func.count(Adoption.id).desc())
    .limit(10)
    .all()

    return render_template("admin/reports.html",
                           title="Relatórios",
                           monthly_data=monthly_data,
                           most_adopted_species=most_adopted_species,
                           most_adopted_breeds=most_adopted_breeds)

# Rota para Exportar CSV de Adoções Confirmadas
@bp.route("/relatorios/exportar_csv", methods=["GET"], endpoint="export_csv")
@login_required
@admin_required
def export_csv():
    # Obter datas do request (se houver)
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    query = Adoption.query.filter(Adoption.status == "Confirmada")

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            query = query.filter(Adoption.data_atualizacao >= start_date)
        if end_date_str:
            # Adiciona 1 dia para incluir a data final completa
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Adoption.data_atualizacao < end_date)
    except ValueError:
        flash("Formato de data inválido. Use AAAA-MM-DD.")
        return redirect(url_for("admin.reports"))

    adoptions = query.order_by(Adoption.data_atualizacao.asc()).all()

    if not adoptions:
        flash("Nenhuma adoção confirmada encontrada no período selecionado.")
        return redirect(url_for("admin.reports"))

    # Gerar CSV
    si = StringIO()
    cw = csv.writer(si)

    # Cabeçalho
    header = ["ID Adoção", "Data Confirmação", "ID Pet", "Nome Pet", "Espécie", "Raça", "ID Adotante", "Nome Adotante", "Email Adotante", "Telefone Adotante"]
    cw.writerow(header)

    # Dados
    for adoption in adoptions:
        pet_nome = adoption.pet.nome if adoption.pet else "N/A"
        pet_especie = adoption.pet.especie if adoption.pet else "N/A"
        pet_raca = adoption.pet.raca if adoption.pet else "N/A"
        adotante_nome = adoption.adotante.nome if adoption.adotante else "N/A"
        adotante_email = adoption.adotante.email if adoption.adotante else "N/A"
        adotante_tel = adoption.adotante.telefone if adoption.adotante else "N/A"

        row = [
            adoption.id,
            adoption.data_atualizacao.strftime("%Y-%m-%d %H:%M:%S"),
            adoption.id_pet,
            pet_nome,
            pet_especie,
            pet_raca,
            adoption.id_adotante,
            adotante_nome,
            adotante_email,
            adotante_tel
        ]
        cw.writerow(row)

    output = si.getvalue()
    si.close()

    # Criar resposta HTTP para download
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=adocoes_confirmadas.csv"}
    )

