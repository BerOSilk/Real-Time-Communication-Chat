from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_socketio import SocketIO
from flask_cors import CORS
import sqlite3 as sql
import pymongo
from chat import module,vars
from api.render import render
from api.update import udt
from api.send import snd
from api.authentication import auth
from api.request_pfp import profile_picture
import datetime as dt
from classes.database import Database

db = Database("database")

app = Flask(__name__)
app.register_blueprint(module)
app.register_blueprint(render)
app.register_blueprint(udt)
app.register_blueprint(snd)
app.register_blueprint(auth)
app.register_blueprint(profile_picture)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/login_redirect')
def login_redirect():
    return redirect(url_for('login', message ='#'))


@app.route('/')
def index():

    logged = list(db.find("logged_in", {"user_agent": request.headers.get('user-Agent')},{"username": 1, "user_agent": 1}))

    if logged != [] and logged[0]["user_agent"]:
        return redirect(url_for('module.main', name = logged[0]["username"]))
    return render_template('index.html',user=vars.getName())


@socketio.on('request_data')
def request_data(data):

    from_user = data['from_user']
    to_user = data['to_user']
    msg = data['msg']
    header = data['header']

    date_now = dt.datetime.now()
    time_now = date_now.strftime('%H:%M')
    
    socketio.emit('receive_data', {'message': msg, 'from_user': to_user, 'time_now': time_now, 'target': from_user, 'header': header})

@socketio.on('send_logout_request')
def logout_request(data):
    socketio.emit('logout_request',data)

@socketio.on('py_login_request')
def py_login_request(data):
    socketio.emit('login_request', data)


if __name__ == '__main__':
    socketio.run(app, debug=True)