from flask import Blueprint,request,make_response,redirect,url_for,jsonify
# from flask_socketio import emit
# import sqlite3 as sql
import gridfs
import re
import datetime as dt
from PIL import Image
# import io
from classes.database import Database

db = Database("database")
fs = gridfs.GridFS(db.get_db())

auth = Blueprint('auth',__name__)

def is_valid_email(email):
    
    res = list(db.find("users",{"email": email},{email: 1}))

    if res != []:
        return 'Email already exists'

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if re.match(email_regex, email):
        return False
    else:
        return 'Email is not valid'

def is_valid_password(password):
    if len(password) < 8:
        return 'password length must be at least 8'
    
    lower_case_regex = r'[a-z]'
    upper_case_regex = r'[A-Z]'
    digit_regex = r'\d'
    

    if not re.search(lower_case_regex, password):
         return 'password must contain at least one lower case letter'
    if not re.search(upper_case_regex, password):
         return 'password must contain at least one upper case letter'
    if not re.search(digit_regex, password):
         return 'password must contain at least one number'
    
    return False

def is_valid_username(username):

    res = list(db.find("users",{"username": username},{"username": 1}))
    print(res)
    if res != []:
        return "username already exists"
    print("username result passed")
    digit_regex = r'\d'
    special_characters_regex = r'[!@#$%^&*(),?":{}|<>]'
    print("variables passed")
    if re.search(digit_regex, username) or re.search(special_characters_regex, username):
        return "username can't contain special characters"
    print(False)
    return False


@auth.route('/auth',methods=['POST'])
def signin():
    data = request.json
    req = data.get('request')
    
    # con = sql.connect('instances/database.db')
    # cur = con.cursor()

    if req == 'signin':

        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember')
        
        psw = list(db.find("users",{"username": username},{"password": 1}))

        # cur.execute("SELECT password FROM users WHERE username = ?",(username,))

        # psw = cur.fetchone()
        if psw == []:
            return '<p>username not found</p>'
        psw = psw[0]["password"]
        if psw == password:
            
            db.insert("logged_in",[{"username": username,"remember": remember,"user_agent": request.headers.get('user-Agent')}])

            # cur.execute("INSERT INTO logged_in VALUES(?,?,?)",(username,remember,request.headers.get('user-Agent'),))
            # con.commit()

            return redirect(url_for('module.main', name=username))
        else:
            return '<p>incorrect password</p>'
    
    elif req == 'signup':
    
        username = data.get('username')
        email    = data.get('email')
        password = data.get('password')

        print("attempting")

        check = is_valid_username(username)

        if check:
            return jsonify({'message': check})
        print("username passed")
        check = is_valid_email(email)

        if check:
            return jsonify({'message': check})
        
        print("email passed")

        check = is_valid_password(password)

        if check:
            return jsonify({'message': check})
        print("password passed")
        now =  dt.datetime.now()
        img_id = -1
        # img = Image.open('')
        with open("static/images/blank-profile-picture.png","rb") as img:
            img_id = fs.put(img,filename="blank_pfp.png")

        db.insert("users",[{
                        "username": username,
                        "password": password,
                        "email": email,
                        "display_name": username,
                        "pfp_id": img_id,
                        "created_at": now,
                        "status": "online"
                        }])
        # cur.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)",(username,password,email,username,byte_array,now,"online"))
        # con.commit()
        # byte_array.close()

        return jsonify({'message': 'success'})
    