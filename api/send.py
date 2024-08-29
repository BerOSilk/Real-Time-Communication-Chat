from flask import Blueprint,request,jsonify
from classes.database import Database
import sqlite3 as sql
import datetime as dt

db = Database("database")

snd =  Blueprint('send',__name__)

# def get_max(max_id):
#     mx_len = 0

#     for msg in max_id:
#         print(type(msg["msg_id"]))
#         print(msg["msg_id"])
#         mx_len = max(mx_len,msg["msg_id"])
#     return mx_len
#     # l = []

#     # for msg in max_id:
#     #     if len(msg["msg_id"]) == mx_len:
#     #         l.append[int(msg["msg_id"])]
    
#     # return max(l)

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

    # max_id = list(db.find("messages",{"from": name,"to": to},{"msg_id": 1}))
    # max_id = get_max(max_id) + 1

    # cur.execute('SELECT msg_id FROM messages ORDER BY msg_id DESC')
    # max_id = int(cur.fetchone()[0]) + 1

    req = data.get('request')

    if req == 'reply':
        db.insert("messages",[{
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