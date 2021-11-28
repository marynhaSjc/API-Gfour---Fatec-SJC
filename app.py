from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory, send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from flask_mysqldb import MySQL,MySQLdb
from sqlalchemy.engine import url
from sqlalchemy.orm import query, sessionmaker
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as db
import mysql.connector
from sqlalchemy.sql import func
from sqlalchemy.orm import lazyload
from sqlalchemy import create_engine,ForeignKey,or_
from sqlalchemy_utils import database_exists, create_database
from app import db
from dotenv import load_dotenv
from sqlalchemy.orm import relationship

load_dotenv(".env")
app = Flask(__name__)

usuario = 'root'
senha = 'fatec2021'
nome_banco = 'dbfatec'
host = 'localhost'


engine = create_engine("mysql://root:fatec2021@localhost/dbfatec")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:fatec2021@localhost/dbfatec'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

if not database_exists(engine.url):
    create_database(engine.url)

association_table = db.Table('Usuario_has_Grupo',db.Model.metadata,
                              db.Column('usuario_idUsuario',db.Integer,db.ForeignKey('Usuario.idUsuario')),
                                db.Column('grupo_idGrupo',db.Integer, db.ForeignKey('Grupo.idGrupo')))

association_usuario_disciplina = db.Table('Usuario_has_Disciplina',db.Model.metadata,
                                db.Column('usuario_idUsuario',db.Integer,db.ForeignKey('Usuario.idUsuario')),
                                db.Column('disciplina_idDisciplina',db.Integer,db.ForeignKey('Disciplina.idDisciplina')))

association_postagem_grupo = db.Table('Postagem_has_Grupo',db.Model.metadata,
                                db.Column('postagem_idPostagem',db.Integer,db.ForeignKey('Postagem.idPostagem')),
                                db.Column('grupo_idGrupo',db.Integer,db.ForeignKey('Grupo.idGrupo')))


class Usuario(db.Model):
    __tablename__="Usuario"
    idUsuario = db.Column(db.Integer, primary_key= True, autoincrement = True)
    nomeUsuario = db.Column(db.String(30))
    emailUsuario = db.Column(db.String(30))
    senhaUsuario = db.Column(db.String(15))
    tipoUsuario = db.Column(db.String(10))
    disciplina = relationship("Disciplina", secondary=association_usuario_disciplina)
    grupo = relationship("Grupo",secondary='Usuario_has_Grupo')
    postagem = relationship("Postagem",cascade="all,delete-orphan")

class Postagem(db.Model):
    __tablename__ = "Postagem"
    idPostagem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataPostagem = db.Column(db.DateTime(timezone=True), server_default=func.now())
    tituloPostagem = db.Column(db.String(100))
    mensagemPostagem = db.Column(db.String(2000))
    usuario_id = db.Column(db.Integer,ForeignKey("Usuario.idUsuario"))
    usuario = relationship("Usuario")
    datafimPostagem = db.Column(db.DateTime())
    anexo = relationship("Anexo", back_populates="postagem")
    grupo = relationship("Grupo", secondary=association_postagem_grupo)
    

class Anexo(db.Model):
    __tablename__ = "Anexo"
    idAnexo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pathfileAnexo = db.Column(db.String(100))
    postagem_id = db.Column(db.Integer,ForeignKey("Postagem.idPostagem",ondelete="CASCADE"))
    postagem = relationship("Postagem",back_populates="anexo",single_parent=True)

class Disciplina(db.Model):
    __tablename__="Disciplina"
    idDisciplina = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomeDisciplina = db.Column(db.String(100))
    usuario = relationship("Usuario", secondary=association_usuario_disciplina)


# class Usuario_has_Disciplina(db.Model):
#     usuario_idUsuario = db.Column(db.Integer,ForeignKey("Usuario.idUsuario"),primary_key=True)
#     disciplina_idDisciplina = db.Column(db.Integer,ForeignKey("Disciplina.idDisciplina"),primary_key=True)

class Funcao(db.Model):
    __tablename__ = "Funcao"
    idFuncao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codFuncao = db.Column(db.String(5))
    nomeFuncao = db.Column(db.String(100))

class Usuario_has_Funcao(db.Model):
    usuario_idUsuario = db.Column(db.Integer,ForeignKey("Usuario.idUsuario"),primary_key=True)
    disciplina_idFuncao = db.Column(db.Integer,ForeignKey("Funcao.idFuncao"),primary_key=True)

class Grupo(db.Model):
    __tablename__ = "Grupo"
    idGrupo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomeGrupo = db.Column(db.String(100))
    usuario = relationship("Usuario",secondary=association_table)
    postagem = relationship("Postagem", secondary=association_postagem_grupo)

db.create_all()


app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = usuario
app.config['MYSQL_PASSWORD'] = senha
app.config['MYSQL_DB'] = nome_banco

mysql = MySQL(app)
documentos = os.getenv("documentos")

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['pwd']
        usuário = Usuario.query.filter_by(nomeUsuario=nome,senhaUsuario=senha).first()
        if usuário:
            # session['loggedin'] = True
            session['nome'] = usuário.nomeUsuario
            session['tipo'] = usuário.tipoUsuario
            session['id'] = str(usuário.idUsuario)
            session['senha'] = usuário.senhaUsuario
            msg = 'Logged in successfully !'
            flash(msg)
            return redirect(url_for('show'))
        else:
            msg = 'Nome Usuário e/ou Senha incorretos  !'
            flash(msg)
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('nome', None)
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    msg = ''
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['pwd']
        if senha != request.form['cpwd']:
            msg = "SENHA DIGITADA NÃO CONFERE"
            flash(msg)
            return render_template('cadastro.html')
        else:
            user = Usuario.query.filter_by(emailUsuario=email).first()
        if user:
            msg = 'Conta já cadastrada !'
            flash(msg)
            return render_template('cadastro.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Endereço de email inválido !'
            flash(msg)
            return render_template('cadastro.html')
        elif not email.split("@")[1] == "fatec.sp.gov.br":
            msg = 'Email não valido !'
            flash(msg)
            return render_template('cadastro.html')
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome do usuário deve conter somente caracteres e numeros !'
            flash(msg)
            return render_template('cadastro.html')
        elif not nome or not senha or not email:
            msg = "Preencha o formulario"
            flash(msg)
            return render_template('cadastro.html')
        else:
            novo_usuario = Usuario(nomeUsuario=nome,emailUsuario=email,senhaUsuario=senha,tipoUsuario="aluno")
            db.session.add(novo_usuario)
            db.session.commit()
            msg = 'Cadastro Efetuado com Sucesso !'
            flash(msg)
    elif request.method == 'POST':
        msg = 'Por favor preencha o formulario'
        flash(msg)
    return redirect(url_for('login'))

@app.route('/login')
def index():
    return render_template('login.html')

@app.route('/postar', methods=['POST', 'GET'])
def postar():
    if request.method == 'POST':
        nome = session['nome']
        novo_post = Postagem(usuario_id=session['id'],
                             titulo=request.form['titulo'],conteudo=request.form['conteudo'])
        if not request.form['titulo']:
            flash("Titulo é obrigatorio") #INSERIR MENSAGENS FLASH NO HTML
            return render_template ('postar.html')
        else:
            db.session.add(novo_post)
            db.session.commit()
    return redirect(url_for('show'))

@app.route('/visualizacao/<id>')
@app.route('/visualizacao')
def show(id=None):
    id_Usuario = session['id']
    podePostar = True if session['tipo'] == "professor" else False
    grupos = Grupo.query.join(association_table).filter(
        (association_table.c.usuario_idUsuario == id_Usuario)&(association_table.c.grupo_idGrupo == Grupo.idGrupo)
    ).all()
    postagem = [] 
    nome_grupo = "Geral"
    if id != None:
        grupo = Grupo.query.filter_by(idGrupo = id).first()
        nome_grupo = grupo.nomeGrupo
        postagem = Postagem.query.join(association_postagem_grupo).filter(
            (association_postagem_grupo.c.grupo_idGrupo == id)&(association_postagem_grupo.c.postagem_idPostagem == Postagem.idPostagem)
        ).all()
    else:   
        postagem = Postagem.query.join(association_postagem_grupo,association_postagem_grupo.c.postagem_idPostagem == None,isouter=True)
    
    return render_template('visualizacao.html', postagem=postagem,
            podePostar=podePostar,id_Usuario=id_Usuario, grupos=grupos,nome_grupo=nome_grupo,tipo=session["tipo"])


@app.route("/localizar",methods=["POST","GET"])
def localizar():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        if search_word == '':
            postagem = Postagem.query.join(Postagem.usuario,aliased=True)
        else:
            postagem = Postagem.query.join(Postagem.usuario, aliased=True).filter(
                or_(
                    Postagem.tituloPostagem.ilike("%"+search_word+"%"),
                    Postagem.mensagemPostagem.ilike("%"+search_word+"%"),
                    Postagem.dataPostagem.ilike("%"+search_word+"%")
                )
            )
            numrows = Postagem.query.join(Postagem.usuario, aliased=True).filter(
                or_(
                    Postagem.tituloPostagem.ilike("%"+search_word+"%"),
                    Postagem.mensagemPostagem.ilike("%"+search_word+"%"),
                    Postagem.dataPostagem.ilike("%"+search_word+"%")
                )
            ).count()
    return jsonify({'htmlresponse': render_template('response.html', postagem=postagem, numrows=numrows)})

@app.route("/cadastrar")
def cadastrar():
    return render_template("cadastro.html")

@app.route("/leitura")
def leitura():
    grupos = Grupo.query.all()
    return render_template('postar.html', grupos=grupos)

@app.route("/pesquisar")
def pesquisar():
    return render_template('pesquisa.html')

@app.route("/arquivos",methods = ["GET"])
def lista_arquivos():
    arquivos = []
    for nome_do_arquivo in os.listdir(documentos):
        endereco_do_arquivo = os.path.join(documentos, nome_do_arquivo)
        if(os.path.isfile(endereco_do_arquivo)):
            arquivos.append(nome_do_arquivo)
    return jsonify(arquivos)

@app.route("/arquivos/<nome_do_arquivo>", methods=["GET,POST"])
def get_arquivo(nome_do_arquivo):
    return send_from_directory(documentos,nome_do_arquivo,as_attachment = False)

@app.route("/apagar/<id>")
def apagar(id):
    usuario_id = session['id']
    postagem = Postagem.query.filter_by(idPostagem=id).first()
    if str(usuario_id) == str(postagem.usuario_id):
        #Postagem.query.filter_by(idPostagem=id).delete()
        db.session.delete(postagem)
        db.session.commit()
        flash("POST APAGADO")
    else:
        flash("SEM PERMISSÂO PARA APAGAR O POST")
    return redirect (url_for('show'))

@app.route("/arquivos",methods=["POST"])
def post_arquivo():
    if request.method == 'POST':
        nome = session['nome']
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        grupos = request.form.getlist('grupos')
        if not titulo:
            flash("Titulo é obrigatorio")  # INSERIR MENSAGENS FLASH NO HTML
            return render_template('postar.html')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        arquivo = request.files.get("meuArquivo")
        nome_do_arquivo = arquivo.filename
        grupos_salvos = []
        for grupo in grupos:
            g=Grupo.query.filter_by(idGrupo=grupo).first()
            grupos_salvos.append(g)
        if nome_do_arquivo != '':
            arquivo.save(os.path.join(documentos, nome_do_arquivo))
            pathFile=nome_do_arquivo  #os.path.join(documentos,nome_do_arquivo)
            novo_post = Postagem(usuario_id=session['id'],grupo=grupos_salvos,
                                 tituloPostagem=request.form['titulo'], mensagemPostagem=request.form['conteudo'])
            db.session.add(novo_post)
            db.session.flush()
            novo_anexo = Anexo(pathfileAnexo=pathFile,postagem_id=novo_post.idPostagem)
            db.session.add(novo_anexo)
            db.session.commit()
            return redirect(url_for('show'))
        else:
            novo_post = Postagem(usuario_id=session['id'],grupo=grupos_salvos,
                                 tituloPostagem=request.form['titulo'], mensagemPostagem=request.form['conteudo'])
            db.session.add(novo_post)
            db.session.commit()
            return redirect(url_for('show'))
    return render_template('postar.html')

@app.route('/admin')
def admin():
    tipo = session["tipo"]
    if tipo== "admin":
        usuarios = Usuario.query.all()
        return render_template('index.html',usuarios=usuarios)
    else:
        return redirect (url_for('show'))
@app.route('/inicio')
def admin_inicio():
    return render_template('index.html')

@app.route("/deletar/<id>")
def deletar(id):
    usuario_id = session['id']
    logado = Usuario.query.filter_by(idUsuario=usuario_id).first()
    if logado.tipoUsuario == 'admin' or logado.tipoUsuario == 'professor':
        user = Usuario.query.filter_by(idUsuario=id).first()
        db.session.delete(user)
        db.session.commit()
        msg = 'Usuario apagado'
        flash(msg)
        return redirect(url_for('admin'))
    else:
        msg = 'Não permitido apagar usuario.'
        flash(msg)
    return redirect(url_for('logout'))

@app.route('/edit/<id>',methods=['GET','POST'])
def edit(id):
    msg = ''
    user = Usuario.query.filter_by(idUsuario=id).first()
    grupos = Grupo.query.all()
    usuario_grupos = []
    for grupo in user.grupo:
        usuario_grupos.append (grupo.idGrupo)
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cargo = request.form['cargo']
        grupos = request.form.getlist('grupos')
        if not user:
            msg = 'Usuario não cadastrado !'
            flash(msg)
            return redirect (url_for ('admin'))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Endereço de email inválido !'
            flash(msg)
            return redirect(url_for('edit',id=id ))
        elif not email.split("@")[1] == "fatec.sp.gov.br":
            msg = 'Email não valido !'
            flash(msg)
            return redirect(url_for('edit',id=id ))
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome do usuário deve conter somente caracteres e numeros !'
            flash(msg)
            return redirect(url_for('edit',id=id ))
        elif not nome or not cargo or not email:
            msg = "Preencha o formulário"
            flash(msg)
            return redirect(url_for('edit',id=id ))
        else:
            g = []
            for id in grupos:
                grupo = Grupo.query.filter_by(idGrupo=id).first()
                g.append(grupo)
            user.nomeUsuario = nome
            user.emailUsuario = email
            user.tipoUsuario = cargo
            user.grupo = g
            db.session.commit()
            msg = 'Alteração Efetuada com Sucesso !'
            flash(msg)
            return redirect(url_for('admin'))
    print(user.tipoUsuario)
    return render_template('edit.html',user=user, grupos=grupos, usuario_grupos = usuario_grupos)

@app.route('/view/<id>')
def view(id):
    usuario = Usuario.query.filter_by(idUsuario=id).first()
    return render_template('view.html',usuario=usuario)

@app.route('/add_grupo', methods=['POST','GET']) 
def add_grupo():
    if request.method == 'POST':
        grupo = request.form['add_grupo']
        novo_grupo = Grupo(nomeGrupo=grupo)
        db.session.add(novo_grupo)
        db.session.commit()
    grupos = Grupo.query.all()
    return render_template ('prototipo.html', grupos=grupos)

if __name__=="__main__":
    app.run(debug=True,port=5000)


