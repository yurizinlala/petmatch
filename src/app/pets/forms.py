# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
# from flask_wtf.file import FileAllowed # Para validação de upload, se implementado

# Opções para campos Select
ESPECIE_CHOICES = [("Cão", "Cão"), ("Gato", "Gato")]
PORTE_CHOICES = [("Pequeno", "Pequeno"), ("Médio", "Médio"), ("Grande", "Grande")]
SEXO_CHOICES = [("Macho", "Macho"), ("Fêmea", "Fêmea")]
STATUS_CHOICES = [("Disponível", "Disponível"), ("Em Adoção", "Em Adoção"), ("Adotado", "Adotado")]

class PetForm(FlaskForm):
    nome = StringField("Nome do Pet", validators=[DataRequired(), Length(min=2, max=80)])
    especie = SelectField("Espécie", choices=ESPECIE_CHOICES, validators=[DataRequired()])
    raca = StringField("Raça", validators=[DataRequired(), Length(min=2, max=80)])
    idade = IntegerField("Idade (meses)", validators=[DataRequired(), NumberRange(min=1, message="Idade deve ser pelo menos 1 mês.")])
    porte = SelectField("Porte", choices=PORTE_CHOICES, validators=[DataRequired()])
    sexo = SelectField("Sexo", choices=SEXO_CHOICES, validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[DataRequired(), Length(min=10, max=1000)])
    # Campo de foto: Por enquanto, vamos usar um campo de texto para URL
    # No futuro, pode ser um FileField para upload
    foto = StringField("URL da Foto", validators=[Optional(), Length(max=500)]) # Campo para URL da foto
    # foto = FileField("Foto do Pet", validators=[Optional(), FileAllowed(["jpg", "png", "jpeg"], "Apenas imagens JPG, JPEG e PNG!")])

    # Status só deve ser editável pelo admin em certos contextos, mas incluímos aqui por enquanto
    # status = SelectField("Status", choices=STATUS_CHOICES, validators=[DataRequired()])

    submit = SubmitField("Salvar Pet")

