function signin_request(){
    username = document.getElementById('username').value
    password = document.getElementById('password').value
    remember = document.getElementById('rememberMe').value
    errors    = document.getElementById('error')

    url = '/auth'
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            request : 'signin',
            username: username,
            password: password,
            remember: remember
        })
    })
    .then(response => {
        if(response.redirected){
            window.location.href = response.url;
        }else{
            return response.text();
        }
    })
    .then(data => {
        errors.innerHTML = data;
    })
    .catch(error => {
        console.log('there was an error signing in', error);
    })

}

function signup_request(){

    username   =    document.getElementById('uname').value
    email      =    document.getElementById('email').value
    password   =    document.getElementById('psw').value
    c_pasword  =    document.getElementById('confirm-psw').value
    errors    = document.getElementById('error')
    
    if(password != c_pasword){
        error.innerHTML = 'passwords do not match';
        return;
    }


    url = '/auth'
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            request   : 'signup'  ,
            username  : username  ,
            email     : email     ,
            password  : password
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.message == 'success'){
            document.querySelector('.container').classList.remove('right-panel-active');
        }else{
            errors.innerHTML = data.message;
        }
    })
    .catch(error => {
        console.log('there was an error signing up', error);
    })
}