from flask import Blueprint,render_template, request, make_response, abort, redirect, url_for
from classes.database import Database
import gridfs


db = Database("database")
fs = gridfs.GridFS(db.get_db())

class Variables:

    def __init__(self,*args):
        self.name = args[0]
    
    def getName(self) -> str:
        return self.name

    def setName(self,name : str) -> None:
        self.name = name

module =  Blueprint('module',__name__)

vars = Variables('')

@module.route('/main/<name>', methods=['POST', 'GET'])
def main(name):

    # con = sql.connect('instances/database.db')
    # cur = con.cursor()
    
    if request.method == 'POST': 
        db.delete_many("logged_in",{"user_agent": request.headers.get('user-Agent')})
        # cur.execute("DELETE FROM logged_in WHERE username = ?",(name,))
        # con.commit()
        vars.name = name
        return redirect('/')

    user_agent = list(db.find("logged_in",{"username": name},{"user_agent": 1}))
    # cur.execute("SELECT user_agent FROM logged_in WHERE username = ?",(name,))
    # 
    # user_agent = cur.fetchone()
    
    if user_agent != []:
        
        user = list(db.find("users",{"username": name}))

        # cur.execute("SELECT username FROM users WHERE username = ?",(name,))

        if user == []:
            return abort(404)

        users = list(db.find("users",{"username": {"$ne": name}},sort=["username",-1]))
        # cur.execute("SELECT * FROM users WHERE username != ? ORDER BY username",(name,))
        # users = cur.fetchall()

        # cur.execute("SELECT username,pfp,display_name,status FROM users WHERE username != ? ORDER BY username",(name,))
        
        users_chat = ""
        user_status = user[0]["status"]

        # cur.execute("SELECT status FROM users WHERE username = ?",(name,))
        # user_status = cur.fetchone()

        user_color = "background-color:"
        match user_status:
            case 'invisible':
                user_color += 'gray'
            case 'online':
                user_color += '#04AA6D'
            case 'idle':
                user_color += 'orange'
            case _:
                user_color += '#f44336'

        for user in users:
            
            # cur.execute("SELECT user_agent FROM logged_in WHERE username = ?",(user[0],))

            logged = list(db.find("logged_in",{"username": user["username"]}))

            color = ''

            if user["status"] == 'invisible' or logged == []:
                color = 'gray'
            elif user["status"]== 'online':
                color = '#04AA6D'
            elif user["status"] == 'idle':
                color = 'orange'
            else:
                color = '#f44336'

            client = db.get_db()
            messages = client["messages"]
            count = messages.count_documents({"from_user": user["username"],"to_user": name,"seen_at": None})
            # cur.execute("SELECT COUNT(*) FROM messages WHERE (from_user = ? AND to_user = ?) AND seen_at IS NULL",(user[0],name,))

            # count = cur.fetchone()[0]
            # img = fs.get(user["pfp_id"])

            users_chat += f'''<div class="name-container" id={user["username"]}>
                                <button type="button" onclick="load(\'{user["username"]}\',\'load\')"><img class=\'pfp\' src="{ url_for('pfp.request_pfp', name = user["username"])}" alt="Profile Picture">
                                <div class="status" style="background-color: {color}"></div>
                                <h2>{user["display_name"]}</h2></button>
                                {f"<div id='new-msg'>{count}</div>" if count != 0 else ""}
                            </div>'''
        
        return render_template('main.html',user=name, users=users_chat,user_color=user_color)
    else:
        return redirect('/')


@module.route('/main/<name>/settings', methods=['GET', 'POST'])
def settings(name):

    # con = sql.connect('instances/database.db')
    # cur = con.cursor()
    # cur.execute("SELECT * FROM users WHERE username =?", (name,))
    # res = cur.fetchone()

    res = list(db.find("users",{"username": name}))

    if request.method == 'POST':
        if "submit-settings" in request.form:
            name = request.form["username"]
            new_psw = request.form['updated-new-psw']

            if 'file' not in request.files:
                f = request.files['profile-picture']

                if f and f.filename != '':
                    
                    file_name = name + '-pfp.png'

                    # f.save('static/images/' + file_name)
                    img_id = fs.put(f,filename=file_name)
                    db.update_one("users",{"username": name},{"$set": {"pfp_id": img_id}})
                    # cur.execute('UPDATE users SET pfp = ? WHERE username = ?',('/static/images/' + file_name,name))
                    # con.commit()
            
            if new_psw != '':

                db.update_one("users",{"username": name},{"password": new_psw})

                # cur.execute('UPDATE users SET password =? WHERE username =?',(new_psw, name))
                # con.commit()

            display_name = request.form['display']

            db.update_one("users",{"username": name},{"$set": {"display_name": display_name}})

            # cur.execute('UPDATE users SET display_name =? WHERE username =?',(display_name, name))
            # con.commit()

            new_status = request.form['status']
            db.update_one("users",{"username": name},{"$set" :{"status": new_status}})

            # cur.execute('UPDATE users SET status =? WHERE username =?',(new_status, name))
            # con.commit()

            return redirect('/')
    return render_template('settings.html',username=name,email=res[0]["email"],display_name=res[0]["display_name"])


