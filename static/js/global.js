function toggle_password_visibility(element_id,button_id) {
    x = document.getElementById(element_id);
    button = document.getElementById(button_id);
    if(x.type == 'password'){
        x.type = 'text'
        button.style.backgroundImage = 'url(\'/static/images/visible.png\')';
    }else{
        x.type = 'password'
        button.style.backgroundImage = 'url(\'/static/images/hide.png\')';
    }
}
