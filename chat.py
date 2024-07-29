from flask import Blueprint,render_template, request, make_response, abort, redirect, url_for
import sqlite3 as sql


module =  Blueprint('module',__name__)


@module.route('/main/<name>', methods=['POST', 'GET'])
def main(name):

    con = sql.connect('instances/database.db')
    cur = con.cursor()

    if request.method == 'POST': 

        # import app
        # app.last_loggedout.append(name)

        con = sql.connect('instances/database.db')
        cur = con.cursor()
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

        cur.execute("SELECT users.username,pfp,display_name,status,loggedTEXT FROM users JOIN logged_in ON users.username = logged_in.username WHERE users.username != ? ORDER BY loggedTEXT DESC",(name,))
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

        for user in users:

            color = ''

            if user[3] == 'Invisible' or user[4] == 'NO':
                color = 'gray'
            elif user[3] == 'Online':
                color = '#04AA6D'
            elif user[3] == 'idle':
                color = 'orange'
            else:
                color = '#f44336'

            users_chat += f'''<div class="name-container" id={user[0]}>
                                <button type="button" onclick="load(\'{user[0]}\',\'load\')"><img class=\'pfp\' src="{user[1]}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user[2]}</h2></button>
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
            cur.execute('UPDATE logged_in SET status =? WHERE username =?',(new_status, name))
            con.commit()

            return redirect('/')
    return render_template('settings.html',username=name,email=res[2],profile_picture=res[4],display_name=res[3])


