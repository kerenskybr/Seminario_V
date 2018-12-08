from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from seminario import db, login_manager, app
from flask_login import UserMixin

#Funçao que controla chaves estrangeiras
@login_manager.user_loader
def load_user(id_usuario):
	return Usuario.query.get(int(id_usuario))

class Usuario(db.Model, UserMixin):
	__tablename__ = 'usuarios'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	nome = db.Column(db.String(30), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	senha = db.Column(db.String(60), nullable=False)
	imagem_perfil = db.Column(db.String(20), nullable=False, default='default.jpg') #no routes account user
	
	#Repr retorna as informaçoes em paralelo com o bd
	def __repr__(self):
		return f"Usuario('{self.nome}', '{self.email}', '{self.imagem_perfil}')"
        
class Pagar(db.Model):
	__tablename__ = 'pagar'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	descpagar = db.Column(db.String(100), nullable=False)
	valorpagar = db.Column(db.Float, nullable=False)
	datapagar = db.Column(db.Date, nullable=False)
	id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False) #chave estrangeira referenciando o id usuario

	usuario = db.relationship('Usuario', backref=db.backref('posts', lazy=True))

	def __repr__(self):
		return f"Pagar('{self.descpagar}', '{self.valorpagar}', '{self.datapagar}',  '{self.usuario}')"

class Receber(db.Model):
	__tablename__ = 'receber'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	descreceber = db.Column(db.String(100), nullable=False)
	valorreceber = db.Column(db.Float, nullable=False)
	datareceber = db.Column(db.Date, nullable=False)
	id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False) #chave estrangeira referenciando o id usuario

	usuario = db.relationship('Usuario', backref=db.backref('usuarios', lazy=True)) # quel é a do maldito POSTS??

	def __repr__(self):
		return f"Receber('{self.descreceber}', '{self.valorreceber}', '{self.datareceber}',  '{self.usuario}')"
