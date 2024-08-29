from flask import Blueprint,request,make_response,redirect,url_for,jsonify,send_file
import gridfs
from io import BytesIO
from classes.database import Database

db = Database("database")
fs = gridfs.GridFS(db.get_db())

profile_picture = Blueprint("pfp",__name__)

@profile_picture.route("/request_pfp/<name>")
def request_pfp(name):
    # con = sql.connect('instances/database.db')
    # cur = con.cursor()

    img_id = list(db.find("users",{"username": name},{"pfp_id": 1}))

    img = fs.find_one(img_id[0]["pfp_id"])

    img_data = BytesIO(img.read())
    img_data.seek(0)

    return send_file(img_data,mimetype='image/png')