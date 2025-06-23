# -*- coding: utf-8 -*-
import re # Import regex for password validation
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Regexp
from src.app.models import User # Ajustado para src

# --- Custom Validators ---
def validate_nome_completo(form, field):
    """Valida se o nome não contém números e tem mais de 6 caracteres."""
    if not field.data or len(field.data) <= 6:
        raise ValidationError("O nome completo deve ter mais de 6 caracteres.")
    if any(char.isdigit() for char in field.data):
        raise ValidationError("O nome completo não pode conter números.")

def validate_endereco(form, field):
    """Valida se o endereço tem mais de 14 caracteres."""
    if not field.data or len(field.data) <= 14:
        raise ValidationError("O endereço deve ter mais de 14 caracteres.")

def validate_password_complexity(form, field):
    """Valida se a senha contém letras e números."""
    password = field.data
    if not password:
        # Let DataRequired handle empty password
        return 
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise ValidationError("A senha deve conter letras e números.")

# --- Forms ---
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message="Campo obrigatório."), Email(message="Email inválido.")])
    password = PasswordField("Senha", validators=[DataRequired(message="Campo obrigatório.")])
    remember_me = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")

class RegistrationForm(FlaskForm):
    # Adicionado campo username
    username = StringField("Nome de Usuário", validators=[
        DataRequired(message="Campo obrigatório."),
        Length(min=3, max=64, message="O nome de usuário deve ter entre 3 e 64 caracteres."),
        Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
               "Nome de usuário deve começar com letra e conter apenas letras, números, _ ou .")
    ])
    nome_completo = StringField("Nome Completo", validators=[
        DataRequired(message="Campo obrigatório."), 
        validate_nome_completo # Custom validator
    ])
    email = StringField("Email", validators=[
        DataRequired(message="Campo obrigatório."), 
        Email(message="Formato de email inválido.")
    ])
    telefone = StringField("Telefone (com DDD)", validators=[
        DataRequired(message="Campo obrigatório."), 
        Length(min=14, max=15, message="Telefone deve estar no formato (XX) XXXXX-XXXX.") # Adjust based on mask
    ]) 
    endereco = TextAreaField("Endereço Completo", validators=[
        DataRequired(message="Campo obrigatório."), 
        validate_endereco # Custom validator
    ])
    password = PasswordField("Senha", validators=[
        DataRequired(message="Campo obrigatório."), 
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres."),
        validate_password_complexity # Custom validator
    ])
    password2 = PasswordField(
        "Repita a Senha", validators=[
            DataRequired(message="Campo obrigatório."), 
            EqualTo("password", message="As senhas não coincidem.")
        ])
    submit = SubmitField("Registrar")

    # Validação customizada para username (check if exists)
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Este nome de usuário já está em uso. Por favor, escolha outro.")

    # Validação customizada para email (check if exists)
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError("Este email já está cadastrado. Por favor, use um email diferente.")
