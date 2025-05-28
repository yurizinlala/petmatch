# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from src.app import db, login # Ajustado para src
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

# Enum para status do Pet (se não for usar string diretamente)
# class PetStatus(enum.Enum):
#     DISPONIVEL = "Disponível"
#     EM_ADOCAO = "Em Adoção"
#     ADOTADO = "Adotado"

# Enum para status da Adoção
# class AdoptionStatus(enum.Enum):
#     PENDENTE = "Pendente"
#     CONFIRMADA = "Confirmada"
#     CANCELADA = "Cancelada"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), index=True, nullable=False)
    cpf = db.Column(db.String(14), index=True, unique=True, nullable=True) # CPF pode ser opcional inicialmente
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.Text, nullable=True) # Campo livre para perfil do adotante
    password_hash = db.Column(db.String(256)) # Aumentado para hashes mais longos
    is_admin = db.Column(db.Boolean, default=False, nullable=False) # Campo para identificar admin
    adocoes = db.relationship("Adoption", backref="adotante", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.nome} ({self.email})>"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(80), nullable=False)
    idade = db.Column(db.Integer, nullable=False) # Em meses
    porte = db.Column(db.String(50), nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    foto_url = db.Column(db.String(500), nullable=True) # URL da foto
    status = db.Column(db.String(50), default="Disponível", nullable=False) # Usando string diretamente
    # status = db.Column(db.Enum(PetStatus), default=PetStatus.DISPONIVEL, nullable=False)
    data_cadastro = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    adocao = db.relationship("Adoption", backref="pet", uselist=False) # Um pet só tem uma adoção ativa/confirmada

    def __repr__(self):
        return f"<Pet {self.nome} ({self.especie} - {self.raca})>"

class Adoption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_pet = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    id_adotante = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data_pedido = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(50), default="Pendente", nullable=False) # Usando string diretamente
    # status = db.Column(db.Enum(AdoptionStatus), default=AdoptionStatus.PENDENTE, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Adoption {self.id} (Pet: {self.id_pet}, Adotante: {self.id_adotante}, Status: {self.status})>"

