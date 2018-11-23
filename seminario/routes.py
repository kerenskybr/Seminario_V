import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, send_file
from seminario import app, db, bcrypt #mail
from seminario.forms import FormDeLogin, FormDeRegistro, FormDeAtualizarConta, FormContasPagar
from seminario.models import Usuario, Pagar
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
plt.style.use('ggplot')

@app.route('/bar_graph/')
def bar_graph():
    fig, ax = plt.subplots()
    df=pd.read_csv("https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/quantreg/gasprice.csv")
    time=df['time']
    gasprice=df['value']
    plt.plot(time,gasprice, color='orange')
    #plt.xlabel("Time (Year)")
    #plt.ylabel("Gas Price")
    #plt.title("Time Series of US Gasoline Prices ")
    canvas = FigureCanvas(fig)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route("/")

@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/sistema")
def sistema():
	return render_template('sistema.html')

@app.route("/registro", methods=['GET', 'POST'])
def registro():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	formulario = FormDeRegistro()
	if formulario.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(formulario.senha.data).decode('utf-8')
		nome = Usuario(nome=formulario.nome.data, email=formulario.email.data, senha=hashed_password)
		db.session.add(nome)
		db.session.commit()
		flash(f'Sua conta foi criada. Você pode agora se logar {formulario.nome.data}!', 'success')
		return redirect(url_for('home'))
	return render_template('registro.html', title='Register', formulario=formulario)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('sistema'))
	formulario = FormDeLogin()
	if formulario.validate_on_submit():
		nome = Usuario.query.filter_by(email=formulario.email.data).first()
		if nome and bcrypt.check_password_hash(nome.senha, formulario.senha.data):
			login_user(nome, remember=formulario.lembrarme.data)
			return redirect(url_for('sistema'))
		else:
			flash('Erro. Nome de usuario ou senha inválido.', 'danger')
	return render_template('login.html', title='login', formulario=formulario)

@app.route("/sair")
def sair():
    logout_user()
    return redirect(url_for('home'))

def salva_imagem(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125) #redimensionando imagens salva espaço e ganha performance
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/minha_conta", methods=['GET', 'POST'])
@login_required
def minha_conta():
	formulario = FormDeAtualizarConta()
	if formulario.validate_on_submit():
		if formulario.imagem.data:
			arquivo_imagem = salva_imagem(formulario.imagem.data)
			current_user.imagem_perfil = arquivo_imagem
		current_user.nome = formulario.nome.data
		current_user.email = formulario.email.data
		db.session.commit()
		flash('Sua conta foi atualizada com sucesso.', 'success')
		return redirect(url_for('minha_conta'))

	elif request.method == 'GET':
		formulario.nome.data = current_user.nome
		formulario.email.data = current_user.email
	imagem_perfil = url_for('static', filename='profile_pics/' + current_user.imagem_perfil)
	return render_template('minha_conta.html', title='Minha Conta', imagem_perfil=imagem_perfil, formulario=formulario)

@app.route("/contas/pagarnovo", methods=['GET', 'POST'])
@login_required
def contas():
	
	
	descricao = Pagar.query.order_by(Pagar.descpagar.desc()).first()
	#descricao_valor = Pagar.query.order_by(Pagar.valorpagar.desc()).first()
	#descricao_data = Pagar.query.order_by(Pagar.datapagar.desc()).first()


	formulario = FormContasPagar()
	if formulario.validate_on_submit():
		pagar = Pagar(descpagar=formulario.descpagar.data, 
			valorpagar=formulario.valorpagar.data, datapagar=formulario.datapagar.data, usuario=current_user) # id_usuario=current_user.id
		db.session.add(pagar)
		db.session.commit()
		flash(f'Valor gravado com sucesso!', 'success')
		

		
		return redirect(url_for('contas'))
	
	return render_template('contas.html', title='contas', formulario=formulario, descricao=descricao)
