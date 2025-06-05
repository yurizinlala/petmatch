# -*- coding: utf-8 -*-
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from datetime import datetime

# Inicialização das extensões
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"  # Rota para redirecionar se não estiver logado
login.login_message = "Por favor, faça login para acessar esta página."
mail = Mail()

# Importar modelos ANTES de create_app para que seed_data esteja disponível
# Mas a definição do user_loader precisa vir DEPOIS da inicialização do login e da importação do User
from src.app import models # Importação geral de models aqui

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa as extensões com a app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app) # LoginManager inicializado aqui
    mail.init_app(app)

    # Importar o modelo User especificamente para o user_loader
    from src.app.models import User

    # Definir o user_loader AQUI, após login.init_app() e importação do User
    @login.user_loader
    def load_user(id):
        # Não é estritamente necessário app_context aqui para user_loader
        return User.query.get(int(id))

    # Registrar Blueprints
    from src.app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from src.app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from src.app.pets import bp as pets_bp
    app.register_blueprint(pets_bp, url_prefix="/pets")

    from src.app.adoptions import bp as adoptions_bp
    app.register_blueprint(adoptions_bp, url_prefix="/adocoes")

    from src.app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Configuração de Logging
    if not app.debug and not app.testing:
        # Log de erros por email
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"].split("@")[-1],
                toaddrs=app.config["ADMINS"],
                subject="Erro na Aplicação PETMATCH",
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # Log em arquivo
        log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = RotatingFileHandler(os.path.join(log_dir, "petmatch.log"), maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("PETMATCH startup")

    # Disponibilizar a função now() para os templates
    @app.context_processor
    def inject_now():
        return {"now": datetime.now}

    # A função seed_data será chamada via comando flask seed
    # models.seed_data(app)

    return app

# A importação geral de models no final não é mais necessária aqui

