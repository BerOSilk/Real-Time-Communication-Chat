from flask import Blueprint,request,jsonify
from classes.database import Database
import sqlite3 as sql
import datetime as dt

db = Database("database")

snd =  Blueprint('send',__name__)

@snd.route('/send', methods=['POST'])
def send():

    data = request.json

    # con = sql.connect('instances/database.db')
    # cur = con.cursor()

    name = data.get('name')
    msg = data.get('msg')
    to = data.get('to')

    date_now = dt.datetime.now()

    time_now = date_now.strftime('%H') + ':' + date_now.strftime('%M')

    max_id = list(db.find("messages",{"msg_id": 1},sort=["msg_id",-1]))

    if max_id == []:
        max_id = 1
    else:
        max_id = int(max_id[0]["msg_id"]) + 1

    # cur.execute('SELECT msg_id FROM messages ORDER BY msg_id DESC')
    # max_id = int(cur.fetchone()[0]) + 1

    req = data.get('request')

    if req == 'reply':
        db.insert("messages",[{
            "msg_id": max_id,
            "from": name,
            "to": to,
            "msg": msg,
            "msg_date": date_now,
            "seen_at": None,
            "reply": data.get('id')
        }])
        # cur.execute('INSERT INTO messages VALUES (?,?,?,?,?,NULL,?)',(max_id,name,to,msg,date_now,data.get('id')))
    else:
        db.insert("messages",[{
            "msg_id": max_id,
            "from": name,
            "to": to,
            "msg": msg,
            "msg_date": date_now,
            "seen_at": None,
            "reply": None
        }])
        # cur.execute('INSERT INTO messages VALUES (?,?,?,?,?,NULL,NULL)',(max_id,name,to,msg,date_now))

    # con.commit()

    return jsonify({'time': time_now})