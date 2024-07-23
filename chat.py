from flask import Blueprint,render_template, request, make_response, abort, redirect, url_for
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
        con.close()

        if not user:
            return abort(404)

        return render_template('main.html',user=name)
    else:
        return redirect(url_for('login', message ='Please Sign In first'))