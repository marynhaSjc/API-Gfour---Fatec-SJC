from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as db
import mysql.connector
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app import db

app = Flask(__name__)

engine = create_engine("mysql://root:fatec2021@localhost/fatec")
if not database_exists(engine.url):
    create_database(engine.url)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:fatec2021@localhost/fatec'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db = SQLAlchemy(app)

    class user(db.Model):
        id = db.Column(db.Integer, primary_key= True, autoincrement = True)
        matricula = db.Column(db.String(30), primary_key =True)
        nome = db.Column(db.String(30))
        email = db.Column(db.String(30))
        senha = db.Column(db.String(15))

    class postagem(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        data = db.Column(db.DateTime(timezone=True), server_default=func.now())
        titulo = db.Column(db.String(100))
        conteudo = db.Column(db.String(2000))
        nome = db.Column(db.String(30))
    db.create_all()

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'fatec2021'
app.config['MYSQL_DB'] = 'fatec'

mysql = MySQL(app)
#documentos = "D:\\DSM_FATEC\\1_Semestre\\api\\Sistema_Fatec\\documentos"

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':# and 'nome' in request.form and 'pwd' in request.form:
        nome = request.form['nome']
        senha = request.form['pwd']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE nome = % s AND senha = % s', (nome, senha,))
        usuário = cursor.fetchone()
        if usuário:
            # session['loggedin'] = True
            session['nome'] = usuário['nome']
            session['senha'] = usuário['senha']
            # msg = 'Logged in successfully !'
            return redirect(url_for('show'))
            # return render_template('show.html', msg=msg)
        else:
            return 'Nome e ou senha invalidos'
            # msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    #session.pop('loggedin', None)
    session.pop('nome', None)
    #session.pop('username', None)
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
            return "SENHA DIGITADA NÃO CONFERE"
        else:

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT nome FROM user WHERE nome = % s', (nome,))
            user = cursor.fetchone()
        if user:

            msg = 'Conta já cadastrada !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Endereço de email inválido !'
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome do usuário deve conter somente caracteres e numeros !'
        elif not nome or not senha or not email:
            msg = "<h1> ´Preencha o formulario</h1>"
         #   flash(msg)
        else:
            cursor.execute('INSERT INTO user  (nome,email,matricula,senha) values (%s, % s, % s, % s)',
                           (nome, email, matricula, senha,))
            mysql.connection.commit()
            msg = 'Cadastro Efetuado com Sucesso !'
    elif request.method == 'POST':
        msg = 'Por favor preencha o formulario'
    return redirect(url_for('login'))
    #return render_template('cadastro.html', msg=msg)


@app.route('/login')
def index():
    return render_template('login.html')


@app.route('/postar', methods=['POST', 'GET'])
def postar():
    if request.method == 'POST':
        nome = session['nome']
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']

        if not titulo:
            flash("Titulo é obrigatorio") #INSERIR MENSAGENS FLASH NO HTML
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO postagem (titulo,conteudo,nome) values (% s, % s, %s)', (titulo, conteudo,nome,))

            mysql.connection.commit()
    return render_template('postar.html')


@app.route('/tela_cheia')
def show():
    nome = session['nome']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM postagem ')
    postagem = cursor.fetchall()
    cursor.close()
    return render_template('visualizacao.html', postagem=postagem)

@app.route('/info')
def info():
    return render_template('tela_info.html')


@app.route("/postagem")
def postagem():
    cur = mysql.connection.cursor()
    postagem = cur.execute("select id,titulo,conteudo,nome from postagem where id = 2")
    
    if postagem > 0:
        postagemDetails = cur .fetchall()
        return render_template("postagem.html" , postagemDetails=postagemDetails)

@app.route("/cadastrar")
def cadastrar():
    return render_template("cadastro.html")
 