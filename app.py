from flask import Flask, render_template, request, redirect, url_for, abort, make_response
import sqlite3 as sql
import re
from chat import module
from flask_mail import Mail, Message

app = Flask(__name__)
app.register_blueprint(module)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '2004.khalilbaraa@gmail.com'
app.config['MAIL_PASSWORD'] = '123456hgf'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

con = sql.connect('instances/database.db')
cur = con.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        display_name TEXT,
        pfp TEXT);
''')

cur.execute('''
        CREATE TABLE IF NOT EXISTS logged_in (
            username TEXT PRIMARY KEY,
            status TEXT,
            remember TEXT
            );
''')

con.commit()
con.close()

def insert(username, password, email):
    con = con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, email,display_name,pfp) VALUES (?,?,?,?,?)", (username, password, email,username,'/static/images/blank-profile-picture.png'))
    cur.execute("INSERT INTO logged_in (username,status,remember,loggedTEXT) VALUES (?,'ONLINE','off','NO')", (username,))
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
        return 'Email is not a valid email address'

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
        rep_password = request.form['psw-repeat']

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

        if check_user:
            cur.execute('SELECT * FROM logged_in WHERE username = ?', (check_user,))
            res = cur.fetchone()

            if res[2] == 'ONLINE':
                return redirect(url_for('module.main', name = check_user))

        res = make_response(redirect(url_for('module.main', name = username)))
        res.set_cookie('myApp', username)

        cur.execute("UPDATE logged_in SET loggedTEXT = 'YES', remember =? WHERE username =?", (remember, username,))
        con.commit()
        con.close()
        return res
    if message == '#':
        message = ''
    return render_template('login.html', Just_Signed=message)


@app.route('/')
def index():
    username = request.cookies.get('myApp')
    if username:
        con = sql.connect('instances/database.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM logged_in WHERE username = ?', (username,))
        res = cur.fetchone()
        print(res[2])
        if res and res[2] == 'on':
            return redirect(url_for('module.main', name = username))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)