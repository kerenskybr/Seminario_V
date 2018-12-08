import os
import datetime
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, send_file, Markup
from seminario import app, db, bcrypt #mail
from seminario.forms import FormDeLogin, FormDeRegistro, FormDeAtualizarConta, FormContasPagar, FormContasReceber
from seminario.models import Usuario, Pagar, Receber
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import func
#Grafico
"""
@app.route("/chart")
def chart():
	labels = ["January","February","March","April","May","June","July","August"]
	values = [10,9,8,7,6,4,7,8]
    return render_template('chart.html', values=values, labels=labels)
"""
@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/sistema")
def sistema():
	labels = ["Jan","Fev","Mar","Abr","Mai","Jun",
	"Jul","Ago","Set", "Out","Nov", "Dez"]
	values = [101]
	#Query dos lançamentos
	query_pagar = db.session.query(func.sum(Pagar.valorpagar)).first()

	query_receber = db.session.query(func.sum(Receber.valorreceber)).first()

	query_receber_for =  Receber.query.filter_by(id_usuario=current_user.id)

	diferenca = float(query_receber[0]) - float(query_pagar[0])


	#Query das mensagens
	#checka = db.session.query(Pagar.datapagar).first()
	

	dia_atual = datetime.date.today()

	check_dia = Pagar.query.filter_by(datapagar=dia_atual).first()
	
	query_dia = Pagar.query.filter_by(id_usuario=current_user.id)


	return render_template('sistema.html', query_pagar=query_pagar[0], query_receber=query_receber[0], 
							query_receber_for=query_receber_for, diferenca=diferenca, dia_atual=dia_atual, 
							query_dia=query_dia, check_dia=check_dia, values=values, labels=labels)

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

@app.route("/calendario")
def calendario():
	return render_template('calendario_simples.html')

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

'''
@app.route("/contas/<conta_id>")
def post(conta_id):
    post = Post.query.get_or_404(conta_id)
    return render_template('post.html', title=post.title, post=post)
'''
@app.route("/contas", methods=['GET', 'POST'])
@login_required
def contas():
	formulario = FormContasPagar()
	formulario_r = FormContasReceber()

	query_pagar = Pagar.query.filter_by(id_usuario=current_user.id)
	query_receber = Receber.query.filter_by(id_usuario=current_user.id)

	if formulario.validate_on_submit():
		pagar = Pagar(descpagar=formulario.descpagar.data, 
			valorpagar=formulario.valorpagar.data, datapagar=formulario.datapagar.data, usuario=current_user) # id_usuario=current_user.id
		db.session.add(pagar)
		db.session.commit()
		db.session.close()
		flash(f'Valor gravado com sucesso!', 'success')	
		return redirect(url_for('contas'))

	if formulario_r.validate_on_submit():

		receber = Receber(descreceber=formulario_r.descreceber.data, 
			valorreceber=formulario_r.valorreceber.data, datareceber=formulario_r.datareceber.data, usuario=current_user) # id_usuario=current_user.id
		db.session.add(receber)
		db.session.commit()
		db.session.close()
		flash(f'Valor gravado com sucesso!', 'success')	
		return redirect(url_for('contas'))


	return render_template('contas.html', title='contas', formulario=formulario, query_pagar=query_pagar,
							formulario_r=formulario_r, query_receber=query_receber)

#Rota que edita e popula a conta 
@app.route("/contas/<conta_id>/editar", methods=['GET', 'POST'])
@login_required
def atualizar_contas_pagar(conta_id):
	
	query_p = Pagar.query.get_or_404(conta_id)
	if query_p.usuario != current_user:
		abort(403)

	formulario = FormContasPagar()
	
	if formulario.validate_on_submit():
		query_p.descpagar = formulario.descpagar.data
		query_p.valorpagar = formulario.valorpagar.data
		query_p.datapagar = formulario.datapagar.data
		db.session.commit()
		flash('Editado com sucesso!')
		return redirect(url_for('contas', conta_id=query_p.id))

	elif request.method == 'GET':
		formulario.descpagar.data = query_p.descpagar
		formulario.valorpagar.data = query_p.valorpagar
		formulario.datapagar.data = query_p.datapagar
		

	return render_template('editar.html', formulario=formulario, query_p=query_p)

@app.route("/contas/<receber_id>/editar_r", methods=['GET', 'POST'])
@login_required
def atualizar_contas_receber(receber_id):

	query_r = Receber.query.get_or_404(receber_id)
	if query_r.usuario != current_user:
		abort(403)

	formulario_r = FormContasReceber()

	if formulario_r.validate_on_submit():
		query_r.descreceber = formulario_r.descreceber.data
		query_r.valorreceber = formulario_r.valorreceber.data
		query_r.datareceber = formulario_r.datareceber.data
		db.session.commit()
		flash('Editado com sucesso!')
		return redirect(url_for('contas', receber_id=query_r.id))

	elif request.method == 'GET':
		formulario_r.descreceber.data = query_r.descreceber
		formulario_r.valorreceber.data = query_r.valorreceber
		formulario_r.datareceber.data = query_r.datareceber

	return render_template('editar_receber.html',formulario_r=formulario_r, query_r=query_r)


@app.route("/contas/<conta_id>/deletar", methods=['POST'])
@login_required
def deletar_pagar(conta_id):
	query_p = Pagar.query.get_or_404(conta_id)
	if query_p.usuario != current_user:
		abort(403)
	db.session.delete(query_p)
	db.session.commit()
	flash('Apagado com sucesso', 'success')
	return redirect(url_for('contas'))

@app.route("/contas/<receber_id>/deletar_r", methods=['POST'])
@login_required
def deletar_receber(receber_id):
	query_r = Receber.query.get_or_404(receber_id)
	if query_r.usuario != current_user:
		abort(403)
	db.session.delete(query_r)
	db.session.commit()
	flash('Apagado com sucesso', 'success')
	return redirect(url_for('contas'))

    