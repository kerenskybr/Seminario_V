from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user, AnonymousUserMixin
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from seminario.models import Usuario, Pagar


class FormDeLogin(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrarme = BooleanField('Lembre-me')
    submit = SubmitField('Logar')

class FormDeRegistro(FlaskForm):
    nome = StringField('Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Cadastrar')

    #Validação para verificar se o usuario ja existe
    def validate_username(self, nome):
        
        usuario = Usuario.query.filter_by(nome=nome.data).first()

        if usuario:
            raise ValidationError("Esse nome de usuario já existe. Favor escolha outro.")

    def validate_email(self, email):
        
        usuario = Usuario.query.filter_by(email=email.data).first()

        if usuario:
            raise ValidationError("Esse email já foi usado. Favor escolha outro.")      

class FormDeAtualizarConta(FlaskForm):
    nome = StringField('Nome de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    imagem = FileField('Atualizar Imagem da Conta.', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Atualizar')

    #Validação para verificar se o usuario ja existe
    def validate_username(self, nome):
        if nome.data != current_user.nome:
            user = Usuario.query.filter_by(nome=nome.data).first()

            if user:
                raise ValidationError("Esse nome de usuario já existe. Favor escolha outro.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Usuario.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError("Esse email já foi usado. Favor escolha outro.")     

class FormContasPagar(FlaskForm):
    descpagar = StringField('Descrição', validators=[DataRequired(), Length(min=2, max=50)])
    valorpagar = FloatField('Valor', validators=[DataRequired()])
    datapagar = DateField('Data a Pagar', validators=[DataRequired()], format='%d/%m/%Y')
    submit = SubmitField('Adicionar')
    submit_editar = SubmitField('Atualizar')