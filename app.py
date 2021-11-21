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
from sqlalchemy import create_engine,ForeignKey
from sqlalchemy_utils import database_exists, create_database
from app import db
#from funcaoBD import criaBD,authMysql
from dotenv import load_dotenv

from sqlalchemy.orm import relationship




load_dotenv(".env")


app = Flask(__name__)

usuario = 'root'
senha = 'fatec2021'
nome_banco = 'fatec'
host = 'localhost'
#criaBD(usuario, senha, nome_banco)

engine = create_engine("mysql://root:fatec2021@localhost/fatec")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:fatec2021@localhost/fatec'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)




if not database_exists(engine.url):
    create_database(engine.url)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key= True, autoincrement = True)
    matricula = db.Column(db.String(30), primary_key =True)
    nome = db.Column(db.String(30))
    email = db.Column(db.String(30))
    senha = db.Column(db.String(15))

class Postagem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.DateTime(timezone=True), server_default=func.now())
    titulo = db.Column(db.String(100))
    conteudo = db.Column(db.String(2000))
    #nome = db.Column(db.String(30))
    usuario_id = db.Column(db.Integer,ForeignKey("user.id"))
    #usuario_post = relationship("User")
    usuario_post = relationship(User, lazy="joined", single_parent=True,remote_side="User.id",uselist=False)
    pathFile = db.Column(db.String(100))
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE nome = % s AND senha = % s', (nome, senha,))
        usuário = cursor.fetchone()
        cursor.close()
        if usuário:
            # session['loggedin'] = True
            session['nome'] = usuário['nome']
            session['id'] = usuário['id']
            session['senha'] = usuário['senha']
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
        matricula = request.form['matricula']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['pwd']
        if senha != request.form['cpwd']:
            msg = "SENHA DIGITADA NÃO CONFERE"
            flash(msg)
            return render_template('cadastro.html')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT matricula FROM user WHERE matricula = % s', (matricula,))
            user = cursor.fetchone()

        if user:
            msg = 'Conta já cadastrada !'
            flash(msg)
            return render_template('cadastro.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Endereço de email inválido !'
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
            cursor.execute('INSERT INTO user  (nome,email,matricula,senha) values (%s, % s, % s, % s)',
                           (nome, email, matricula, senha,))
            mysql.connection.commit()
            cursor.close()
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
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # cursor.execute('INSERT INTO postagem (titulo,conteudo,usuario_id) values (% s, % s, %s)', (titulo, conteudo,usuario_id,))
            db.session.add(novo_post)
            db.session.commit()

    return redirect(url_for('show'))


@app.route('/visualizacao')
def show():
    nome = session['nome']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''SELECT postagem.id AS postagem_id, postagem.data AS postagem_data, postagem.titulo AS postagem_titulo, postagem.conteudo AS postagem_conteudo, postagem.
usuario_id AS postagem_usuario_id, postagem.`pathFile` AS `postagem_pathFile`, user_1.id AS user_1_id, user_1.matricula AS user_1_matricula, user_1.nome
 AS user_1_nome, user_1.email AS user_1_email, user_1.senha AS user_1_senha
FROM postagem INNER JOIN user AS user_2 ON user_2.id = postagem.usuario_id LEFT OUTER JOIN user AS user_1 ON user_1.id = postagem.usuario_id order by postagem_data  DESC 
''')
    postagem = cursor.fetchall()
    cursor.close()

    #postagem = Postagem.query.join(Postagem.usuario_post,aliased=True)


    #print(postagem)

    return render_template('visualizacao.html', postagem=postagem)


@app.route("/localizar",methods=["POST","GET"])
def localizar():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            query = "SELECT * from postagem ORDER BY id"
            cursor.execute(query)
            postagem = cursor.fetchall()
            cursor.close()
        else:
            query = ''' SELECT * from postagem
             WHERE titulo LIKE '%{}%'
             OR conteudo LIKE '%{}%'
              OR data LIKE '%{}%'
              ORDER BY id DESC LIMIT 20'''.format(search_word,search_word,search_word)
            #query = "SELECT * from postagem WHERE titulo LIKE '%{}%' OR conteudo LIKE '%{}%' OR nome LIKE '%{}%' OR data LIKE '%{}%' ORDER BY id DESC LIMIT 20".format(search_word,search_word,search_word,search_word)
            cursor.execute(query)
            numrows = int(cursor.rowcount)
            postagem = cursor.fetchall()
            print(numrows)

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



    #return render_template('visualizacao.html', postagem=postagem)

#@app.route("/downloads",methods=["GET"])
#def download_file():
    #filename = request.form['filename']
    #print ('filename')
#return img
#return send_file(documentos,file,  as_attachment = True)
    #return send_from_directory(documentos,filename,as_attachment = True)



@app.route("/prototipo")
def prototipo():
    return render_template('prototipo.html')


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
                                 titulo=request.form['titulo'], conteudo=request.form['conteudo'],
                                 pathFile=pathFile)
            db.session.add(novo_post)
            db.session.commit()
            return redirect(url_for('show'))
        else:
            novo_post = Postagem(usuario_id=session['id'],
                                 titulo=request.form['titulo'], conteudo=request.form['conteudo'])
            db.session.add(novo_post)
            db.session.commit()
            return redirect(url_for('show'))
    return render_template('postar.html')


if __name__=="__main__":
    app.run(debug=True,port=8000)
