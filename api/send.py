from flask import Blueprint,request,jsonify
import sqlite3 as sql
import datetime as dt


snd =  Blueprint('send',__name__)

@snd.route('/send', methods=['POST'])
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