from flask import Blueprint,render_template, request, make_response, abort, redirect, url_for, jsonify
import sqlite3 as sql

module =  Blueprint('module',__name__)

@module.route('/main/<name>', methods=['POST', 'GET'])
def main(name):
    con = sql.connect('instances/database.db')
    cur = con.cursor()

    if request.method == 'POST':
        cur.execute("UPDATE logged_in SET logged_in = 'NO', remember='off' WHERE username = ?",(name,))
        con.commit()
        res = make_response(redirect('/'))
        res.set_cookie('myApp','',0)
        return res
    


    cur.execute("SELECT logged_in FROM logged_in WHERE username = ?", (name,))
    logged = cur.fetchone()

    if not logged:
        return abort(404)
    
    if logged[0] == 'YES':

        cur.execute("SELECT username FROM users WHERE username =?", (name,))
        user = cur.fetchone()

        if not user:
            return abort(404)

        cur.execute("SELECT * FROM logged_in WHERE username != ?",(name,))
        users = cur.fetchall()

        users_chat = ""

        for user in users:
            users_chat += f'''<div class="name-container">
                                <img class=\'pfp\' src="/static/images/blank-profile-picture.png" alt="Profile Picture">
                                <div class="status" style="background-color: {'gray' if user[1] == 'NO' else '#04AA6D'}"></div>
                                <h2>{user[0]}</h2>
                            </div>'''

        return render_template('main.html',user=name, users=users_chat)
    else:
        return redirect(url_for('login', message ='Please Sign In first'))

@module.route('/render')
def data():

    name = request.args.get('name', '')
    value = request.args.get('value', '')
    value += '%'
    con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM logged_in WHERE username like ? and username != ?",(value,name,))
    users = cur.fetchall()

    print(users)

    users_chat = ''
    
    for user in users:
        users_chat += f'<div class="name-container"><img class=\'pfp\' src="/static/images/blank-profile-picture.png" alt="Profile Picture"><div class="status" style="background-color: {'gray' if user[1] == 'NO' else '#04AA6D'}"></div><h2>{user[0]}</h2></div>'

    return users_chat