from flask import Blueprint,render_template, request, make_response, abort, redirect, url_for, jsonify
import sqlite3 as sql
from flask_mail import Mail, Message 
import re
import os

module =  Blueprint('module',__name__)



@module.route('/main/<name>', methods=['POST', 'GET'])
def main(name):
    con = sql.connect('instances/database.db')
    cur = con.cursor()

    if request.method == 'POST':
        cur.execute("UPDATE logged_in SET status = 'OFFLINE', loggedTEXT='NO', remember='off' WHERE username = ?",(name,))
        con.commit()
        res = make_response(redirect('/'))
        res.set_cookie('myApp','',0)
        return res
    


    cur.execute("SELECT loggedTEXT FROM logged_in WHERE username = ?", (name,))
    logged = cur.fetchone()

    if not logged:
        return abort(404)
    
    if logged[0] != 'NO':

        cur.execute("SELECT username FROM users WHERE username =?", (name,))
        user = cur.fetchone()

        if not user:
            return abort(404)

        cur.execute("SELECT * FROM logged_in WHERE username != ?",(name,))
        users_logged_in = cur.fetchall()

        cur.execute("SELECT pfp,display_name FROM users WHERE username != ?",(name,))
        users = cur.fetchall()

        users_chat = ""

        cur.execute("SELECT status FROM logged_in WHERE username = ?",(name,))
        user_status = cur.fetchone()[0]

        user_color = "background-color:"

        if user_status == "Invisible":
            user_color += 'gray'
        elif user_status == 'Online':
            user_color += '#04AA6D'
        elif user_status == 'idle':
            user_color += 'orange'
        else:
            user_color += '#f44336'

        for logged,user in zip(users_logged_in,users):

            color = ''

            if logged[1] == 'INVISIBLE' or logged[3] == 'NO':
                color = 'gray'
            elif logged[1] == 'ONLINE':
                color = '#04AA6D'
            elif logged[1] == 'idle':
                color = 'orange'
            else:
                color = '#f44336'

            users_chat += f'''<div class="name-container">
                                <img class=\'pfp\' src="{user[0]}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user[1]}</h2>
                            </div>'''

        cur.execute('SELECT pfp from users where username = ?',(name,))
        pfp = cur.fetchone()

        return render_template('main.html',user=name, users=users_chat,pfp_path=pfp[0],user_color=user_color)
    else:
        return redirect(url_for('login', message ='Please Sign In first'))


@module.route('/main/<name>/settings', methods=['GET', 'POST'])
def settings(name):

    con = sql.connect('instances/database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username =?", (name,))
    res = cur.fetchone()

    if request.method == 'POST':
        if "submit-settings" in request.form:
            name = request.form["username"]
            new_psw = request.form['updated-new-psw']

            if 'file' not in request.files:
                f = request.files['profile-picture']

                if f and f.filename != '':
                    
                    file_name = name + '-pfp.png'

                    f.save('static/images/' + file_name)

                    cur.execute('UPDATE users SET pfp = ? WHERE username = ?',('/static/images/' + file_name,name))
                    con.commit()
            
            if new_psw != '':
                cur.execute('UPDATE users SET password =? WHERE username =?',(new_psw, name))
                con.commit()

            display_name = request.form['display']

            cur.execute('UPDATE users SET display_name =? WHERE username =?',(display_name, name))
            con.commit()

            new_status = request.form['status']
            print(new_status)
            cur.execute('UPDATE logged_in SET status =? WHERE username =?',(new_status, name))
            con.commit()

            return redirect('/')
    return render_template('settings.html',username=name,email=res[2],profile_picture=res[4],display_name=res[3])

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
        users_chat += f'<div class="name-container"><img class=\'pfp\' src="/static/images/blank-profile-picture.png" alt="Profile Picture"><div class="status" style="background-color: {'gray' if user[1] == 'OFFLINE' else '#04AA6D'}"></div><h2>{user[0]}</h2></div>'

    return users_chat

def is_valid_password(password):
    check_list = ['green' for i in range(4)]
    if len(password) < 8:
        return False
    
    lower_case_regex = r'[a-z]'
    upper_case_regex = r'[A-Z]'
    digit_regex = r'\d'
    

    if not re.search(lower_case_regex, password) or not re.search(upper_case_regex, password) or not re.search(digit_regex, password):
        return False
    
    return True

@module.route('/update',methods=['POST'])
def update():
    data = request.json
    passed = data.get('button')

    con = sql.connect('instances/database.db')
    cur = con.cursor()

    if passed == 'Cancel':
        ret_form = f'<div><h1>Change Password</h1><form method="POST"><div class="form-group"><label id="old-psw">Old Password <label id="old-psw-error"></label> </label><input type="text" id="old-psw-input" name="old-psw" placeholder="old password"></div><div class="form-group"><label id="new-psw">new Password <label id="new-psw-error"></label></label><input type="text" id="new-psw-input" name="new-psw" placeholder="new password"></div><div class="form-group"><label id="confirm-psw">confirm Password <label id="confirm-psw-error"></label></label><input type="text" id="confirm-psw-input" name="confirm-psw" placeholder="confirm password"></div><div class="form-group"><button type="button" name="submit-settings" onclick="change(\'Update\')">Change</button></div></form></div>'
        return ret_form

    if passed == 'Update':
        old_psw = data.get('old_psw')

        cur.execute('SELECT password FROM users WHERE username = ?',(data.get('user'),))
        res = cur.fetchone()

        if res[0] != old_psw:
            return jsonify({'message': 'Incorrect password'})
        
        new_psw = data.get('new_psw')

        if not is_valid_password(new_psw):
            return jsonify({'message': 'Password must contain at least 8 characters, including uppercase, lowercase, and numbers'})
    
        confirm_psw = data.get('confirm_psw')

        if new_psw != confirm_psw:
            return jsonify({'message': 'Passwords do not match'})
        
        return jsonify({'message': new_psw})



