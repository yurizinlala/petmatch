# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from src.app.models import User # Ajustado para src

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember_me = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")

class RegistrationForm(FlaskForm):
    nome = StringField("Nome Completo", validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    telefone = StringField("Telefone (com DDD)", validators=[DataRequired(), Length(min=10, max=15)]) # Simples validação de tamanho
    endereco = TextAreaField("Endereço Completo", validators=[DataRequired(), Length(min=10, max=255)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        "Repita a Senha", validators=[DataRequired(), EqualTo("password", message="As senhas devem ser iguais.")])
    submit = SubmitField("Registrar")

    # Validação customizada para email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Este email já está cadastrado. Por favor, use um email diferente.")

# Poderíamos adicionar um formulário de edição de perfil aqui depois
# class EditProfileForm(FlaskForm):
#     nome = StringField("Nome Completo", validators=[DataRequired(), Length(min=3, max=100)])
#     telefone = StringField("Telefone (com DDD)", validators=[DataRequired(), Length(min=10, max=15)])
#     endereco = TextAreaField("Endereço Completo", validators=[DataRequired(), Length(min=10, max=255)])
#     perfil = TextAreaField("Sobre você (Perfil do Adotante)", validators=[Length(max=500)])
#     submit = SubmitField("Salvar Alterações")

