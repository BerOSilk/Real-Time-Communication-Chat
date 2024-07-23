from flask import Flask, render_template, request, redirect, url_for, abort, make_response
import sqlite3 as sql
import re
from chat import module

app = Flask(__name__)
app.register_blueprint(module)

con = sql.connect('instances/database.db')
cur = con.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE);
''')

cur.execute('''
        CREATE TABLE IF NOT EXISTS logged_in (
            username TEXT PRIMARY KEY,
            logged_in TEXT,
            remember TEXT
            );
''')

con.commit()
con.close()

def insert(username, password, email):
    con = con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, email) VALUES (?,?,?)", (username, password, email,))
    cur.execute("INSERT INTO logged_in (username,logged_in,remember) VALUES (?,'NO','off')", (username,))
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

    if re.search(digit_regex, username):
        return "username can't contain digits"
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


# @app.route('/<name>', methods=['POST','GET'])
# def logged_in(name):

#     con = sql.connect('database/database.db')
#     cur = con.cursor()

#     if request.method == 'POST':
#         cur.execute("UPDATE logged_in SET logged_in = 'NO', remember='off' WHERE username = ?",(name,))
#         con.commit()
#         res = make_response(redirect('/'))
#         res.set_cookie('myApp','',0)
#         return res
    


#     cur.execute("SELECT logged_in FROM logged_in WHERE username = ?", (name,))
#     logged = cur.fetchone()

#     if not logged:
#         return abort(404)
    
#     if logged[0] == 'YES':

#         cur.execute("SELECT email FROM users WHERE username =?", (name,))
#         user = cur.fetchone()
#         con.close()

#         if not user:
#             return abort(404)

#         return render_template('main.html',user=name,email=user[0])
#     else:
#         return redirect(url_for('login', message ='Please Sign In first'))

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

            if res[2] == 'on':
                return redirect(url_for('main', name = check_user))

        res = make_response(redirect(url_for('module.main', name = username)))
        res.set_cookie('myApp', username)

        cur.execute("UPDATE logged_in SET logged_in = 'YES', remember =? WHERE username =?", (remember, username,))
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

        if res[2] == 'on':
            return redirect(url_for('module.main', name = username))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)