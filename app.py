from flask import Flask, render_template, request, redirect, url_for
from api.request_pfp import profile_picture
from classes.database import Database
from flask_socketio import SocketIO
from api.authentication import auth
from api.render import render
from chat import module,vars
from flask_cors import CORS
from api.update import udt
from api.send import snd
import datetime as dt
'''

main imports : 

flask : 
---Flask -> The flask object implements a WSGI application and acts as the central object.
---render_template -> Render a template by name with the given context.
---request -> Request variable
---redirect -> Create a redirect response object.
---url_for -> Generate a URL to the given endpoint with the given values.

api.* : API blueprints to register them in the flask app.

classes.database : the database object impelemnts the database.


'''

# the main database 
db = Database("database")

# initalizing the main flask app
app = Flask(__name__)

# registering all blueprints
app.register_blueprint(profile_picture)
app.register_blueprint(module)
app.register_blueprint(render)
app.register_blueprint(udt)
app.register_blueprint(snd)
app.register_blueprint(auth)

# initializing socketio app so emit actions betwenn backend and frontend
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

'''
the main app route.

if the user already signed in from the same device it will again sign him in to continue.

otherwise it will show the sign-in & sign-up page.

'''
@app.route('/')
def index():
    # requesting the logged_in data from the database to check if he's logged in or not and if he has the remember option on or off
    logged = list(db.find("logged_in", {"user_agent": request.headers.get('user-Agent')}))
    # a condition to check if the list is not empty and the user_agent is the right one and if remember is on
    if logged != [] and logged[0]["user_agent"] and logged[0]["remember"] == "on":
        #returning a redirect to the main page with his username
        return redirect(url_for('module.main', name = logged[0]["username"]))
    # otherwise it will render the sign-in & sign-up page.
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