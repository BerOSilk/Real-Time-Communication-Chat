from flask import Blueprint,request,jsonify
from classes.database import Database
import re
 
db = Database("database")

udt =  Blueprint('update',__name__)

def is_valid_password(password):
    if len(password) < 8:
        return False
    
    lower_case_regex = r'[a-z]'
    upper_case_regex = r'[A-Z]'
    digit_regex = r'\d'
    

    if not re.search(lower_case_regex, password) or not re.search(upper_case_regex, password) or not re.search(digit_regex, password):
        return False
    
    return True

@udt.route('/update',methods=['POST'])
def update():
    data = request.json
    passed = data.get('button')

    # con = sql.connect('instances/database.db')
    # cur = con.cursor()

    if passed == 'Cancel':
        ret_form = f'<div><h1>Change Password</h1><form method="POST"><div class="form-group"><label id="old-psw">Old Password <label id="old-psw-error"></label> </label><input type="text" id="old-psw-input" name="old-psw" placeholder="old password"></div><div class="form-group"><label id="new-psw">new Password <label id="new-psw-error"></label></label><input type="text" id="new-psw-input" name="new-psw" placeholder="new password"></div><div class="form-group"><label id="confirm-psw">confirm Password <label id="confirm-psw-error"></label></label><input type="text" id="confirm-psw-input" name="confirm-psw" placeholder="confirm password"></div><div class="form-group"><button type="button" name="submit-settings" onclick="change(\'Update\')">Change</button></div></form></div>'
        return ret_form

    if passed == 'Update':
        old_psw = data.get('old_psw')

        res = list(db.find("users",{"username": data.get('user')},{"password": 1}))

        # cur.execute('SELECT password FROM users WHERE username = ?',(data.get('user'),))
        # res = cur.fetchone()

        if res[0]["password"] != old_psw:
            return jsonify({'message': 'Incorrect password'})
        
        new_psw = data.get('new_psw')

        if not is_valid_password(new_psw):
            return jsonify({'message': 'Password must contain at least 8 characters, including uppercase, lowercase, and numbers'})
    
        confirm_psw = data.get('confirm_psw')

        if new_psw != confirm_psw:
            return jsonify({'message': 'Passwords do not match'})
        
        return jsonify({'message': new_psw})
    