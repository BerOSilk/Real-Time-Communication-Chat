from flask import Blueprint,render_template, request, make_response, abort, redirect, url_for, jsonify
import sqlite3 as sql
from flask_mail import Mail, Message 
import re
import os
import datetime as dt


module =  Blueprint('module',__name__)



@module.route('/main/<name>', methods=['POST', 'GET'])
def main(name):
    con = sql.connect('instances/database.db')
    cur = con.cursor()

    if request.method == 'POST':
        cur.execute("UPDATE logged_in SET loggedTEXT='NO', remember='off' WHERE username = ?",(name,))
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

        cur.execute("SELECT pfp,display_name,username FROM users WHERE username != ?",(name,))
        users = cur.fetchall()

        users_chat = ""

        cur.execute("SELECT status FROM logged_in WHERE username = ?",(name,))
        user_status = cur.fetchone()[0]

        user_color = "background-color:"

        match user_status:
            case 'Invisible':
                user_color += 'gray'
            case 'Online':
                user_color += '#04AA6D'
            case 'idle':
                user_color += 'orange'
            case _:
                user_color += '#f44336'

        for logged,user in zip(users_logged_in,users):

            color = ''

            if logged[1] == 'Invisible' or logged[3] == 'NO':
                color = 'gray'
            elif logged[1] == 'Online':
                color = '#04AA6D'
            elif logged[1] == 'idle':
                color = 'orange'
            else:
                color = '#f44336'

            users_chat += f'''<div class="name-container">
                                <button type="button" onclick="load(\'{user[2]}\',\'load\')"><img class=\'pfp\' src="{user[0]}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user[1]}</h2></button>
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
    con = sql.connect('instances/database.db')
    cur = con.cursor()
    req = request.args.get('request')
    if req == 'search':
        name = request.args.get('name', '')
        value = request.args.get('value', '')
        value = '%' + value + '%'
        
        cur.execute("SELECT status,loggedTEXT FROM logged_in JOIN users ON logged_in.username = users.username WHERE (display_name like ? or users.username like ?) and users.username != ?",(value,value,name,))
        users_status = cur.fetchall()

        cur.execute("SELECT pfp,display_name,username FROM users WHERE (display_name like ? or username like ?) and username!=?",(value,value,name,))
        users_settings = cur.fetchall()


        users_chat = ''
        
        for logged,user in zip(users_status,users_settings):

            color = ''

            if logged[0] == 'INVISIBLE' or logged[1] == 'NO':
                color = 'gray'
            elif logged[0] == 'ONLINE':
                color = '#04AA6D'
            elif logged[0] == 'idle':
                color = 'orange'
            else:
                color = '#f44336'

            users_chat += f'''<div class="name-container">
                                <button type="button" onclick="load(\'{user[2]}\',\'load\')"><img class=\'pfp\' src="{user[0]}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user[1]}</h2></button>
                              </div>
                            '''

        return users_chat
    elif req == 'load-profile':
        target = request.args.get('target')
        cur.execute('SELECT username,pfp,display_name FROM users WHERE username = ?',(target,))
        res = cur.fetchone()

        response = f'''
        <div class="user-info-container">
            <img src="{res[1]}" alt="pfp.png" id="side-profile-img">
            <h1>{res[0]}</h1>
            <h4>{res[2]}</h4>
        </div>
        <div class="line"></div>
        <div class="general-info-container">
            MORE COMING SOON
        </div>

        '''
        
        return response
    elif req == 'load-chat':
        target = request.args.get('target')
        username = request.args.get('name')

        cur.execute('SELECT * FROM messages WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?) ORDER BY msg_date',(target,username,username,target,))
        res = cur.fetchall()
        cur.execute('SELECT username,pfp FROM users WHERE username = ? or username = ?',(target,username))
        users_pfp = cur.fetchall()
        response = ''

        last = ''

        for msg in res:

            pfp = ''

            if msg[0] == users_pfp[0][0]:
                pfp = users_pfp[0][1]
            else:
                pfp = users_pfp[1][1]

            date = dt.datetime.strptime(msg[3], '%Y-%m-%d %H:%M:%S.%f')

            now_date = dt.datetime.now()

            time = date.strftime('%H') + ':' + date.strftime("%M") 

            if date.strftime('%Y-%m-%d') != last:
                if date.strftime('%Y-%m-%d') == now_date.strftime('%Y-%m-%d'):
                    response += f'<div class="time">today</div>'
                elif date.strftime('%Y-%m') == now_date.strftime('%Y-%m') and int(now_date.strftime('%d')) - int(date.strftime('%d')) == 1:
                    response += f'<div class="time">yesterday</div>'
                else:
                    response += f'<div class="time">{date.strftime('%Y/%m/%d')}</div>'
                last = date.strftime('%Y-%m-%d')

            response += f'''

                <div class="message">
                    <img src="{pfp}" alt="pfp" class="profile-pic">
                    <div class="message-content">
                        <div class="message-header">
                            <span class="person">{msg[0]}</span>
                            <span class="timestamp">{time}</span>
                        </div>
                        <div class="text">{msg[2]}</div>
                    </div>
                </div>
                '''
            
    return response




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
    

@module.route('/send', methods=['POST'])
def send():

    data = request.json

    con = sql.connect('instances/database.db')
    cur = con.cursor()

    name = data.get('name')
    msg = data.get('msg')
    to = data.get('to')

    date_now = dt.datetime.now()

    time_now = date_now.strftime('%H') + ':' + date_now.strftime('%M')

    cur.execute('INSERT INTO messages VALUES (?,?,?,?)',(name,to,msg,date_now))
    con.commit()

    return jsonify({'time': time_now})