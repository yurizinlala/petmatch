# -*- coding: utf-8 -*-
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# Removido login_manager daqui para evitar import circular
from src.app import db 
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    nome_completo = db.Column(db.String(120))
    cpf = db.Column(db.String(14), unique=True) # Formato XXX.XXX.XXX-XX
    telefone = db.Column(db.String(15)) # Formato (XX) XXXXX-XXXX
    endereco = db.Column(db.Text)
    perfil_adotante = db.Column(db.Text) # Campo livre para descrever o perfil
    is_admin = db.Column(db.Boolean, default=False)
    adocoes = db.relationship('Adocao', backref='adotante', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# A função load_user foi movida para __init__.py para evitar import circular
# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False) # Cão, Gato
    raca = db.Column(db.String(100))
    idade = db.Column(db.Integer) # Em anos
    porte = db.Column(db.String(50)) # Pequeno, Médio, Grande
    sexo = db.Column(db.String(10)) # Macho, Fêmea
    descricao = db.Column(db.Text)
    foto = db.Column(db.Text) # URL da foto ou nome do arquivo
    status = db.Column(db.String(20), default='disponível', index=True) # disponível, em processo, adotado
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    adocoes = db.relationship('Adocao', backref='pet', lazy='dynamic')

    def __repr__(self):
        return f'<Pet {self.nome} ({self.especie})>'

class Adocao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    adotante_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pendente', index=True) # pendente, aprovada, rejeitada
    data_decisao = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Adocao {self.id} - Pet: {self.pet_id}, Adotante: {self.adotante_id}, Status: {self.status}>'

def seed_data(app):
    with app.app_context():
        logger.info("Verificando necessidade de popular dados iniciais...")
        
        # Verificar se já existe um usuário administrador
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            logger.info("Criando usuário administrador padrão...")
            admin = User(
                username="admin",
                email="admin@petmatch.com",
                nome_completo="Administrador do Sistema",
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            logger.info("Usuário administrador criado com sucesso!")
        
        # Verificar se existem pets cadastrados
        if Pet.query.first() is None:
            logger.info("Banco de dados de pets vazio. Adicionando pets de exemplo...")
            pets_exemplo = [
                {
                    "nome": "Max e Mia",
                    "especie": "Cão",
                    "raca": "Golden Retriever (Filhotes)",
                    "idade": 0, # Meses
                    "porte": "Médio (quando adultos)",
                    "sexo": "Macho e Fêmea",
                    "descricao": "Dois filhotes de Golden Retriever muito brincalhões e amorosos. Procuram um lar juntos ou separados, cheio de carinho e espaço para correr.",
                    "foto": "golden_puppies.jpeg",
                    "status": "disponível"
                },
                {
                    "nome": "Rajado",
                    "especie": "Gato",
                    "raca": "SRD (Sem Raça Definida)",
                    "idade": 2,
                    "porte": "Médio",
                    "sexo": "Macho",
                    "descricao": "Um gato tigrado muito charmoso e independente. Adora um carinho na hora certa e um bom lugar para observar o movimento.",
                    "foto": "cat_tongue.webp",
                    "status": "disponível"
                },
                 {
                    "nome": "Luna",
                    "especie": "Cão",
                    "raca": "Vira-lata Caramelo",
                    "idade": 1,
                    "porte": "Médio",
                    "sexo": "Fêmea",
                    "descricao": "Luna é uma cachorrinha muito dócil e companheira. Se dá bem com outros animais e adora passear. Precisa de um lar com amor e paciência.",
                    "foto": "brown_dog_closeup.jpeg", # Adicionada foto baixada
                    "status": "disponível"
                },
                {
                    "nome": "Simba",
                    "especie": "Gato",
                    "raca": "SRD (Sem Raça Definida)",
                    "idade": 3,
                    "porte": "Grande",
                    "sexo": "Macho",
                    "descricao": "Simba é um gatão laranja muito tranquilo e carinhoso. Perfeito para quem busca um companheiro calmo para relaxar no sofá.",
                    "foto": None, # Adicionar nome da foto se baixar uma
                    "status": "disponível"
                }
            ]

            try:
                for pet_data in pets_exemplo:
                    novo_pet = Pet(
                        nome=pet_data["nome"],
                        especie=pet_data["especie"],
                        raca=pet_data["raca"],
                        idade=pet_data["idade"],
                        porte=pet_data["porte"],
                        sexo=pet_data["sexo"],
                        descricao=pet_data["descricao"],
                        foto=pet_data["foto"],
                        status=pet_data["status"]
                    )
                    db.session.add(novo_pet)
                
                db.session.commit()
                logger.info(f"{len(pets_exemplo)} pets de exemplo adicionados com sucesso!")
            except Exception as e:
                logger.error(f"Erro ao adicionar pets de exemplo: {e}")
                db.session.rollback()
        else:
            logger.info("Banco de dados de pets já contém dados. Nenhuma ação necessária.")
