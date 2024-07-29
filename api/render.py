from flask import Blueprint,request
import sqlite3 as sql
import datetime as dt

render =  Blueprint('render',__name__)

@render.route('/render')
def data():
    con = sql.connect('instances/database.db')
    cur = con.cursor()
    req = request.args.get('request')
    if req == 'search':
        name = request.args.get('name', '')
        value = request.args.get('value', '')
        value = '%' + value + '%'
        
        cur.execute("SELECT users.username,pfp,display_name,status,loggedTEXT FROM logged_in JOIN users ON logged_in.username = users.username WHERE (display_name like ? or users.username like ?) and users.username != ? ORDER BY loggedTEXT DESC",(value,value,name,))
        users = cur.fetchall()


        users_chat = ''
        
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

            users_chat += f'''<div class="name-container">
                                <button type="button" onclick="load(\'{user[0]}\',\'load\')"><img class=\'pfp\' src="{user[1]}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user[2]}</h2></button>
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
