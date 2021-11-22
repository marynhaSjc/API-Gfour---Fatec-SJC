from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory, send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from flask_mysqldb import MySQL,MySQLdb
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as db
import mysql.connector
from sqlalchemy.sql import func
from sqlalchemy.orm import lazyload
from sqlalchemy import create_engine,ForeignKey,or_
from sqlalchemy_utils import database_exists, create_database
from app import db
#from funcaoBD import criaBD,authMysql
from dotenv import load_dotenv

from sqlalchemy.orm import relationship




load_dotenv(".env")


app = Flask(__name__)

usuario = 'root'
senha = 'fatec2021'
nome_banco = 'dbfatec'
host = 'localhost'
#criaBD(usuario, senha, nome_banco)

engine = create_engine("mysql://root:fatec2021@localhost/dbfatec")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:fatec2021@localhost/dbfatec'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)




if not database_exists(engine.url):
    create_database(engine.url)

class Usuario(db.Model):
    __tablename__="Usuario"
    idUsuario = db.Column(db.Integer, primary_key= True, autoincrement = True)
    #matricula = db.Column(db.String(30), primary_key =True)
    nomeUsuario = db.Column(db.String(30))
    emailUsuario = db.Column(db.String(30))
    senhaUsuario = db.Column(db.String(15))
    tipoUsuario = db.Column(db.String(10))

class Postagem(db.Model):
    __tablename__ = "Postagem"
    idPostagem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataPostagem = db.Column(db.DateTime(timezone=True), server_default=func.now())
    tituloPostagem = db.Column(db.String(100))
    mensagemPostagem = db.Column(db.String(2000))
    #nome = db.Column(db.String(30))
    usuario_id = db.Column(db.Integer,ForeignKey("Usuario.idUsuario"))
    usuario = relationship("Usuario")
    #usuario_post = relationship("Usuario")
    #usuario_post = relationship(Usuario, lazy="joined", single_parent=True, remote_side="Usuario.id", uselist=False)
    #pathFile = db.Column(db.String(100))
    datafimPostagem = db.Column(db.DateTime())
    anexo = relationship("Anexo", back_populates="postagem")

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

class Usuario_has_Disciplina(db.Model):
    usuario_idUsuario = db.Column(db.Integer,ForeignKey("Usuario.idUsuario"),primary_key=True)
    disciplina_idDisciplina = db.Column(db.Integer,ForeignKey("Disciplina.idDisciplina"),primary_key=True)

class Funcao(db.Model):
    __tablename__ = "Funcao"
    idFuncao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codFuncao = db.Column(db.String(5))
    nomeFuncao = db.Column(db.String(100))

class Usuario_has_Funcao(db.Model):
    usuario_idUsuario = db.Column(db.Integer,ForeignKey("Usuario.idUsuario"),primary_key=True)
    disciplina_idFuncao = db.Column(db.Integer,ForeignKey("Funcao.idFuncao"),primary_key=True)



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
            print(usuário.nomeUsuario)
            session['nome'] = usuário.nomeUsuario
            session['tipo'] = usuário.tipoUsuario
            session['id'] = str(usuário.idUsuario)
            session['senha'] = usuário.senhaUsuario
            #msg = 'Logged in successfully !'
            #flash(msg)
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
        #matricula = request.form['matricula']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['pwd']
        if senha != request.form['cpwd']:
            msg = "SENHA DIGITADA NÃO CONFERE"
            flash(msg)
            return render_template('cadastro.html')
        else:
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # cursor.execute('SELECT matricula FROM user WHERE matricula = % s', (matricula,))
            # user = cursor.fetchone()
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
        # usuario_id = session['id']
        # titulo = request.form['titulo']
        # conteudo = request.form['conteudo']
        novo_post = Postagem(usuario_id=session['id'],
                             titulo=request.form['titulo'],conteudo=request.form['conteudo'])


        if not request.form['titulo']:
            flash("Titulo é obrigatorio") #INSERIR MENSAGENS FLASH NO HTML
            return render_template ('postar.html')
        else:
            db.session.add(novo_post)
            db.session.commit()

    return redirect(url_for('show'))


@app.route('/visualizacao')
def show():
    id_Usuario = session['id']
    podePostar = True if session['tipo'] == "professor" else False
    postagem = Postagem.query.join(Postagem.usuario,aliased=True)
    return render_template('visualizacao.html', postagem=postagem,podePostar=podePostar,id_Usuario=id_Usuario)


@app.route("/localizar",methods=["POST","GET"])
def localizar():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            postagem = Postagem.query.join(Postagem.usuario,aliased=True)

        else:
            # query = ''' SELECT * from Postagem
            #  WHERE titulo LIKE '%{}%'
            #  OR conteudo LIKE '%{}%'
            #   OR data LIKE '%{}%'
            #   ORDER BY id DESC LIMIT 20'''.format(search_word,search_word,search_word)
            # cursor.execute(query)
            # numrows = int(cursor.rowcount)
            # postagem = cursor.fetchall()
            # print(numrows)
            postagem = Postagem.query.join(Postagem.usuario, aliased=True).filter(
                or_(
                    Postagem.tituloPostagem.ilike("%"+search_word+"%"),
                    Postagem.mensagemPostagem.ilike("%"+search_word+"%")
                )
            )
            print(postagem)
            numrows = Postagem.query.join(Postagem.usuario, aliased=True).filter(
                or_(
                    Postagem.tituloPostagem.ilike("%"+search_word+"%"),
                    Postagem.mensagemPostagem.ilike("%"+search_word+"%")
                )
            ).count()


    return jsonify({'htmlresponse': render_template('response.html', postagem=postagem, numrows=numrows)})

@app.route('/info')
def info():
    return render_template('template_prototipos/tela_info.html')

@app.route("/cadastrar")
def cadastrar():
    return render_template("cadastro.html")

@app.route("/leitura")
def leitura():

    return render_template('postar.html')

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


@app.route("/prototipo")
def prototipo():
    return render_template('prototipo.html')

@app.route("/apagar/<id>")
def apagar(id):
    usuario_id = session['id']
    postagem = Postagem.query.filter_by(idPostagem=id).first()
    print(usuario_id,postagem.usuario_id)
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

        if not titulo:
            flash("Titulo é obrigatorio")  # INSERIR MENSAGENS FLASH NO HTML
            return render_template('postar.html')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        arquivo = request.files.get("meuArquivo")
        nome_do_arquivo = arquivo.filename
        if nome_do_arquivo != '':
            arquivo.save(os.path.join(documentos, nome_do_arquivo))
            pathFile=nome_do_arquivo  #os.path.join(documentos,nome_do_arquivo)
            # cursor.execute('INSERT INTO postagem (titulo,conteudo,,pathFile) values (%s, % s, %s, %s)', (titulo, conteudo, nome, pathFile,))
            # #cursor.execute('INSERT INTO postagem (pathFile) values (%s)', (pathFile,))
            # mysql.connection.commit()
            # cursor.close()
            novo_post = Postagem(usuario_id=session['id'],
                                 tituloPostagem=request.form['titulo'], mensagemPostagem=request.form['conteudo'])

            db.session.add(novo_post)
            db.session.flush()
            novo_anexo = Anexo(pathfileAnexo=pathFile,postagem_id=novo_post.idPostagem)
            db.session.add(novo_anexo)
            db.session.commit()
            return redirect(url_for('show'))
        else:
            novo_post = Postagem(usuario_id=session['id'],
                                 tituloPostagem=request.form['titulo'], mensagemPostagem=request.form['conteudo'])
            db.session.add(novo_post)
            db.session.commit()
            return redirect(url_for('show'))
    return render_template('postar.html')


if __name__=="__main__":
    app.run(debug=True,port=8000)
