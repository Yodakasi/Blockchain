from flask import *
from flask_mysqldb import MySQL
import hashlib
import random
from blockchain import block, blockChain
import os
import threading


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_HTTPONLY'] = False
mysql = MySQL(app)

# MySQL configurations
mysql.app.config['MYSQL_USER'] = 'root'
mysql.app.config['MYSQL_PASSWORD'] = 'toor'
mysql.app.config['MYSQL_DB'] = 'dupcoin'
mysql.app.config['MYSQL_HOST'] = 'localhost'

actualBlockChain = blockChain(4)

def checkChainValidity():
    if actualBlockChain.validateChain():
        return True
    else:
        actualBlockChain.chainReset()
        return False

def setInterval(func, sec):
    def funcWrapper():
        setInterval(func, sec)
        func()
    t = threading.Timer(sec, funcWrapper)
    t.start()
    return t

def hash(notHashed):
    salt = ''.join(chr(random.randint(34,126)) for i in range(8))
    hash = hashlib.sha256((notHashed + salt).encode())
    return hash.hexdigest() + '!' + salt

def verifyhash(hashed, password):
    splited = hashed.split("!")
    if hashlib.sha256((str(password) + splited[1]).encode()).hexdigest() == splited[0]:
        return True
    return False

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.form.get('login'):
        login = request.form.get('login')
        password = request.form.get('password')
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute('''SELECT password FROM `users` WHERE login=%s''', (login))
            if verifyhash(cur.fetchall()[0][0], password):
                session['user'] = login
                return redirect(url_for('user'))
            else:
                message = "Bad login or password <a href='/'>wróć</a>"
        except:
            message = "Server error <a href='/'>wróć</a>"
        return render_template_string(message)
    else:
        return render_template('login.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.form.get('loginreg'):
        login = request.form.get('loginreg')
        email = request.form.get('emailreg')
        password = hash(str(request.form.get('passwordreg')))
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute('''SELECT * FROM `users` WHERE login=%s''', (login))
            elo = len(str(cur.fetchall()))
            if elo > 2:
                message = "login taken <a href='/'>wróć</a>"
            else:
                cur.execute('''INSERT INTO `users` (`id`, `login`, `email`, `password`) VALUES (NULL, %s, %s, %s)''', (login, email, password))
                conn.commit()
                message = "Registration successful <a href='/'>wróć</a>"
        except:
            message = "Registration not successful <a href='/'>wróć</a>"
        return render_template_string(message)
    else:
        return render_template('register.html')

@app.route('/user', methods=['POST', 'GET'])
def user():
    if 'user' in session:
        user = session['user']
        balance1 = actualBlockChain.getAdressBalance(user)
        if request.form.get('adress'):
            amount = int(request.form.get('amount'))
            if int(actualBlockChain.getAdressBalance(user)) > amount and amount > 0 and request.form.get('adress') != user:
                actualBlockChain.newTransaction(user, request.form.get('adress'), request.form.get('amount'))
        if int(actualBlockChain.getAdressBalance(user)) > 1000000 and actualBlockChain.validateChain():
            balance1 = "RSCTF_{F1RST_MILLION$$_U_H$VE_TO_STEAL}"
        return render_template('user.html', username=user, balance=balance1)
    else:
        return redirect('/')

@app.route('/sendblock', methods = ['POST'])
def postJsonHandler():
    content = request.get_json()
    actualBlockChain.addBlockFromClient(json.dumps(content, default=lambda o: o.__dict__))
    return 'JSON posted'

@app.route('/getblock', methods = ['GET'])
def getJsonHandler():
    if 'user' in session:
        user = session['user']
        if len(actualBlockChain.transactionsQueue) > 0:
            return json.dumps(actualBlockChain.newBlockSchema(user), default=lambda o: o.__dict__)
    return render_template_string("nope"), 204

if __name__ == "__main__":
    setInterval(checkChainValidity, 10)
    app.run(host='0.0.0.0')
