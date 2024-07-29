from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_socketio import SocketIO
from flask_cors import CORS
import sqlite3 as sql
import re
from chat import module
from api.render import render
from api.update import udt
from api.send import snd
import datetime as dt


app = Flask(__name__)
app.register_blueprint(module)
app.register_blueprint(render)
app.register_blueprint(udt)
app.register_blueprint(snd)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

last_loggedout = ''

def insert(username, password, email):
    con = con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, email,display_name,pfp) VALUES (?,?,?,?,?)", (username, password, email,username,'/static/images/blank-profile-picture.png'))
    cur.execute("INSERT INTO logged_in (username,status,remember,loggedTEXT) VALUES (?,'Online','off','NO')", (username,))
    con.commit()
    con.close()

def is_valid_email(email):
    con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email,))
    res = cur.fetchone()
    con.close()

    if res:
        return 'Email already exists'

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if re.match(email_regex, email):
        return False
    else:
        return 'Email is not valid'

def is_valid_password(password):
    check_list = ['green' for i in range(4)]
    if len(password) < 8:
        check_list[0] = 'red'
    
    lower_case_regex = r'[a-z]'
    upper_case_regex = r'[A-Z]'
    digit_regex = r'\d'
    

    if not re.search(lower_case_regex, password):
        check_list[1] = 'red'
    if not re.search(upper_case_regex, password):
        check_list[2] = 'red'
    if not re.search(digit_regex, password):
        check_list[3] = 'red'
    
    return check_list

def is_valid_username(username):
    con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("SELECT username FROM users WHERE username = ?", (username,))
    res = cur.fetchone()
    con.close()

    if res:
        return "username already exists"

    digit_regex = r'\d'
    special_characters_regex = r'[!@#$%^&*(),?":{}|<>]'

    if re.search(digit_regex, username) or re.search(special_characters_regex, username):
        return "username can't contain special characters"
    return False


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['uname']
        email = request.form['email']
        password = request.form['psw']
        rep_password = request.form['confirm-psw']

        valid_username = is_valid_username(username)

        if valid_username:
            return render_template('register.html', not_valid_username = valid_username)

        valid_email = is_valid_email(email)

        if valid_email:
            return render_template('register.html', not_valid_email = valid_email)

        valid_password = is_valid_password(password)

        rules = [
            ['password length must be at least 8'],
            ['password must contain at least one lowercase letter'],
            ['password must contain at least one uppercase letter'],
            ['password must contain at least one digit']
            ]

        for i in valid_password:
            if i == 'red':
                return render_template('password_rules.html', rules = rules)

        if rep_password != password:
            return render_template('register.html', not_valid_rep_psw = 'Passwords do not match')

        insert(username, password, email)
        return redirect(url_for('login', message ='Signed up successfully'))

    return render_template('register.html')

@app.route('/login_redirect')
def login_redirect():
    return redirect(url_for('login', message ='#'))

@app.route('/login/<message>',methods=['POST','GET'])
def login(message='#'):
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']
        remember = request.form['remember']

        con = sql.connect('instances/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username =?", (username,))
        user = cur.fetchone()

        if not user:
            return render_template('login.html', invalid_user='Username does not exist')

        if user[1] != password:
            return render_template('login.html', invalid_password='Incorrect password')

        check_user = request.cookies.get('myApp')
        cur.execute('SELECT status FROM logged_in WHERE username = ?', (username,))
        res = cur.fetchone()
        if check_user:
            cur.execute('SELECT loggedTEXT FROM logged_in WHERE username = ?', (check_user,))
            x = cur.fetchone()
            if x[0] == 'YES':
                return redirect(url_for('module.main', name = check_user))

        socketio.emit('login_request',{'user' : username, 'status': res[0]})
        # socketio.emit('logout_request',{'user' : username})

        res = make_response(redirect(url_for('module.main', name = username)))
        res.set_cookie('myApp', username)

        cur.execute("UPDATE logged_in SET loggedTEXT = 'YES', remember =? WHERE username =?", (remember, username,))
        con.commit()
        con.close()
        return res
    if message == '#':
        message = ''
    return render_template('login.html', Just_Signed=message)


@app.route('/',methods=['GET','POST'])
def index():

    if request.method == 'POST':
        if 'sign-in' in request.form:
            username = request.form['uname']
            password = request.form['psw']
            remember = request.form['remember']

            con = sql.connect('instances/database.db')
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username =?", (username,))
            user = cur.fetchone()

            if not user:
                return render_template('login.html', invalid_user='Username does not exist')

            if user[1] != password:
                return render_template('login.html', invalid_password='Incorrect password')

            check_user = request.cookies.get('myApp')
            cur.execute('SELECT status FROM logged_in WHERE username = ?', (username,))
            res = cur.fetchone()
            if check_user:
                cur.execute('SELECT loggedTEXT FROM logged_in WHERE username = ?', (check_user,))
                x = cur.fetchone()
                if x[0] == 'YES':
                    return redirect(url_for('module.main', name = check_user))

            socketio.emit('login_request',{'user' : username, 'status': res[0]})
            # socketio.emit('logout_request',{'user' : username})

            res = make_response(redirect(url_for('module.main', name = username)))
            res.set_cookie('myApp', username)

            cur.execute("UPDATE logged_in SET loggedTEXT = 'YES', remember =? WHERE username =?", (remember, username,))
            con.commit()
            con.close()
            return res
        if 'sign-up' in request.form:
            username = request.form['uname']
            email = request.form['email']
            password = request.form['psw']
            rep_password = request.form['confirm-psw']

            valid_username = is_valid_username(username)

            if valid_username:
                return render_template('register.html', not_valid_username = valid_username)

            valid_email = is_valid_email(email)

            if valid_email:
                return render_template('register.html', not_valid_email = valid_email)

            valid_password = is_valid_password(password)

            rules = [
                ['password length must be at least 8'],
                ['password must contain at least one lowercase letter'],
                ['password must contain at least one uppercase letter'],
                ['password must contain at least one digit']
                ]

            for i in valid_password:
                if i == 'red':
                    return render_template('password_rules.html', rules = rules)

            if rep_password != password:
                return render_template('register.html', not_valid_rep_psw = 'Passwords do not match')

            insert(username, password, email)
            return redirect(url_for('login', message ='Signed up successfully'))
    
    
    username = request.cookies.get('myApp')
    if username:
        con = sql.connect('instances/database.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM logged_in WHERE username = ?', (username,))
        res = cur.fetchone()
        if res and res[2] == 'on':
            return redirect(url_for('module.main', name = username))
    # for user in last_loggedout:
    #     socketio.emit('send_logout_request', { 'user': user })
    # last_loggedout = []
    return render_template('index.html')


@socketio.on('request_data')
def request_data(data):

    from_user = data['from_user']
    to_user = data['to_user']
    msg = data['msg']

    date_now = dt.datetime.now()
    time_now = date_now.strftime('%H:%M')
    
    socketio.emit('receive_data', {'message': msg, 'from_user': to_user, 'time_now': time_now, 'target': from_user})

@socketio.on('send_logout_request')
def logout_request(data):
    user = data['user']
    socketio.emit('logout_request',{'user': user})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')