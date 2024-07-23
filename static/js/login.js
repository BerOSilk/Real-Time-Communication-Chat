
function toggle_password_visibility(){
    x = document.getElementById('psw')
    if(x.type == 'password'){
        x.type = 'text'
    }else{
        x.type = 'password'
    }
}
