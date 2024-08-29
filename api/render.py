from flask import Blueprint,request,jsonify,url_for
from classes.database import Database
import sqlite3 as sql
import datetime as dt

db = Database('database')

render =  Blueprint('render',__name__)

@render.route('/render')
def data():
    # con = sql.connect('instances/database.db')
    # cur = con.cursor()

    req = request.args.get('request')
    if req == 'search':
        name = request.args.get('name', '')
        value = request.args.get('value', '')
        value_regex = {'$regex': value, '$options': 'i'}
        query = {
            "$or":[
                {"display_name": value_regex},
                {"username": value_regex}
            ],
            "username": {"$ne": name}
            }
        attributes = {
                "username": 1,
                "display_name": 1,
                "status": 1
            }
        users = list(db.find("users",query,attributes))

        # cur.execute("SELECT users.username,pfp,display_name,status FROM users WHERE (display_name like ? or users.username like ?) and users.username != ?",(value,value,name,))
        # users = cur.fetchall()


        users_chat = ''
        
        for user in users:
            
            logged = list(db.find("logged_in",{"username": user["username"]},{"user_agent": 1}))

            # cur.execute("SELECT user_agent FROM logged_in WHERE username = ?",(user[0],))
            # logged = cur.fetchone()

            color = ''

            if user["status"] == 'invisible' or logged == []:
                color = 'gray'
            elif user["status"] == 'online':
                color = '#04AA6D'
            elif user["status"] == 'idle':
                color = 'orange'
            else:
                color = '#f44336'

            users_chat += f'''<div class="name-container" id={user["username"]}>
                                <button type="button" onclick="load(\'{user["username"]}\',\'load\')"><img class=\'pfp\' src="{ url_for('pfp.request_pfp', name = user["username"])}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user["display_name"]}</h2></button>
                              </div>
                            '''

        return users_chat
    elif req == 'load-profile':
        target = request.args.get('target')

        res = list(db.find("users", {"username": target}, {"username": 1, "display_name": 1}))[0]

        # cur.execute('SELECT username,pfp,display_name FROM users WHERE username = ?',(target,))
        # res = cur.fetchone()

        response = f'''
        <div class="user-info-container">
            <img src="{ url_for('pfp.request_pfp', name = res["username"])}" alt="pfp.png" id="side-profile-img">
            <h1>{res["username"]}</h1>
            <h4>{res["display_name"]}</h4>
        </div>
        <div class="line"></div>
        <div class="general-info-container">
            <button type="button">pinned messages</button>
            <button type="button">search</button>
            <button type="button">media</button>
            <button type="button" class="green">add friend</button>
            <button type="button" class="red">block</button>
            <button type="button" class="red">report</button>
            
        </div>

        '''
        
        return response
    elif req == 'load-chat':
        target = request.args.get('target')
        username = request.args.get('name')

        query = {
            "$or": [
                {
                    "from": target,
                    "to": username
                },
                {
                    "from": username,
                    "to": target
                }
            ]
        }

        res = db.find("messages",query,sort=["msg_date",1])
        # cur.execute('SELECT * FROM messages WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?) ORDER BY msg_date',(target,username,username,target,))
        # res = cur.fetchall()

        response = ''

        last = ''

        now_date = dt.datetime.now()

        db.update_many("messages",{"from": target,"to": username},{"$set": {"seen_at": now_date}})
        # cur.execute('UPDATE messages SET seen_at = ? WHERE from_user = ? AND to_user = ?',(now_date,target,username))
        # con.commit()

        for msg in res:
            

            # cur.execute('SELECT pfp FROM users WHERE username = ?',(msg[1],))

            # pfp = cur.fetchone()[0]

            date = msg["msg_date"]

            time = date.strftime('%H') + ':' + date.strftime("%M") 


            user = ''

            if msg["reply"]:

                to = list(db.find("messages",{"_id": msg["_id"]},{"from": 1}))[0]

                # cur.execute("SELECT from_user FROM messages WHERE msg_id = ? ",(msg[6],))
                # to = cur.fetchone()[0]
                if msg["from"] == to["from"]:
                    to["from"] = 'himself'
                user = msg["from"] + ' Replied to ' + to["from"]
            else:
                user = msg["from"]


            if date.strftime('%Y-%m-%d') != last:
                if date.strftime('%Y-%m-%d') == now_date.strftime('%Y-%m-%d'):
                    response += f'<div class="time">today</div>'
                elif date.strftime('%Y-%m') == now_date.strftime('%Y-%m') and int(now_date.strftime('%d')) - int(date.strftime('%d')) == 1:
                    response += f'<div class="time">yesterday</div>'
                else:
                    response += f'<div class="time">{date.strftime('%Y/%m/%d')}</div>'
                last = date.strftime('%Y-%m-%d')

            response += f'''

                <div id="message{msg["_id"]}" class="message">
                    <img src="{ url_for('pfp.request_pfp', name = msg["from"])}" alt="pfp" class="profile-pic">
                    <div class="message-content">
                        <div class="message-header">
                            <span class="person">{user}</span>
                            <span class="timestamp">{time}</span>
                        </div>
                        <div class="text">{msg["msg"]}</div>
                    </div>
                    <div id="{msg["_id"]}" style="visibility: hidden"  class="menu">
                        <div class="menu-item" onclick="editMessage()"  ><i class="fa fa-edit"></i></div>
                        <div class="menu-item" onclick="deleteMessage()"><i class="fa fa-trash-o"></i></div>
                        <div class="menu-item" onclick="reply('{str(msg["_id"])}')"><i class="fa fa-reply"></i></div>
                    </div>
                </div>
                '''

        return response
    elif req == 'load-id':
        target = request.args.get('target')
        username = request.args.get('name')

        query = {
            "$or": [
                {
                    "from": target,
                    "to": username
                },
                {
                    "from": username,
                    "to": target
                }
            ]
        }

        res = list(db.find("messages",query,sort=["msg_date",1]))

        l = []

        for i in res:
            l.append(str(i["_id"]))
        # print(l)
        # cur.execute('SELECT msg_id FROM messages WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?) ORDER BY msg_date',(target,username,username,target,))
        # res = cur.fetchall()
        
        return jsonify({'id': l})