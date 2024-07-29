document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight

function fetchData(value,request){

    const name = document.getElementById('user').textContent;
    const url = `/render?value=${encodeURIComponent(value)}&name=${name}&request=${request}`

    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.getElementById('users-container').innerHTML = data;
        });
}


document.addEventListener('DOMContentLoaded',()=>{
    const search = document.getElementById("user-search");
    search.addEventListener('input', () => {
        fetchData(search.value,'search');
    });

   

});


function load_chat(target, request) {
    const name = document.getElementById('user').textContent;
    const url = `/render?name=${name}&request=${request}-chat&target=${target}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            const mc = document.getElementById('messages-container');
            mc.innerHTML = data;
            mc.scrollTop = mc.scrollHeight;
        })
        .catch(error => {
            console.error('There was a problem loading chat:', error);
        });
}

function load_profile(target, request) {
    const url = `/render?request=${request}-profile&target=${target}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            const upc = document.getElementById('user-profile-container');
            upc.style.visibility = 'visible';
            upc.innerHTML = data;
        })
        .catch(error => {
            console.error('There was a problem loading user profile:', error);
        });
}

function load(target, request) {

    let active_user = document.querySelector('.active-user')

    if(active_user){
        active_user.className = "name-container"
    }

    let side_user = document.getElementById(target)

    side_user.className = 'name-container active-user'

    load_profile(target, request);
    load_chat(target, request);
}

document.getElementById('chat-message-input').addEventListener('keydown', (event) => {
    if(event.code == 'Enter'){
        send_message()
    }
})


function createMessageElement(fromUser, textContent, timeContent, pfp_src) {
    const message = document.createElement('div');
    message.className = 'message';

    const img = document.createElement('img');
    img.className = 'profile-pic';
    img.alt = 'pfp';
    img.src = pfp_src;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    const messageHeader = document.createElement('div');
    messageHeader.className = 'message-header';

    const person = document.createElement('span');
    person.className = 'person';
    person.textContent = fromUser;

    const timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    timestamp.textContent = timeContent;

    const text = document.createElement('div');
    text.className = 'text';
    text.textContent = textContent;

    messageHeader.appendChild(person);
    messageHeader.appendChild(timestamp);

    messageContent.appendChild(messageHeader);
    messageContent.appendChild(text);

    message.appendChild(img);
    message.appendChild(messageContent);

    return message;
}


io().on('receive_data', (data) => {
    let user_check = document.getElementById('user')
    if (user_check.textContent == data.from_user){
        let active_chat = document.getElementById(data.target)
        if(active_chat.className.indexOf('active-user') != -1){
            let pfp_src = active_chat.querySelector('.pfp').src
            const message = createMessageElement(data.target, data.message, data.time_now, pfp_src);
            document.getElementById('messages-container').appendChild(message);
            document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight
        }
    }
});

function send_message() {
    const user = document.getElementById('user').textContent;
    const chatInput = document.getElementById('chat-message-input');
    const sentTo = document.querySelector('.user-info-container h1').textContent;

    const message = createMessageElement(user, chatInput.value, '',document.getElementById('user-pfp').src);

    document.getElementById('messages-container').appendChild(message);

    fetch('/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: user,
            msg: chatInput.value,
            to: sentTo
        })
    })
    .then(response => response.json())
    .then(data => {
        message.querySelector('.timestamp').textContent = data.time;
    })
    .catch(error => {
        console.error('Error sending message:', error);
    });

    io().emit('request_data', { to_user: sentTo, msg: chatInput.value, from_user: user });

    chatInput.value = '';
    document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight
}

io().on('login_request', (data) => {
    let user_side = document.getElementById(data.user);
    if(user_side){
        let status = user_side.querySelector('.status');
        if(status){
            switch(data.status){
                case 'Online':
                    status.style.backgroundColor = '#04AA6D';
                    break;
                case 'Invisible':
                    status.style.backgroundColor = 'gray';
                    break;
                case 'idle':
                    status.style.backgroundColor = 'orange';
                    break;
                default:
                    status.style.backgroundColor = '#f44336';
            }
        }
    }
})

io().on('logout_request', (data) =>{
    let user_side = document.getElementById(data.user);
    if(user_side){
        let status = user_side.querySelector('.status');
        if(status){
            status.style.backgroundColor = 'gray';
        }
    }
}) 


function send_logout_request(){
    let user = document.getElementById('user').textContent
    io().emit('send_logout_request', { user: user });

    const url = `/main/${user}`
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user: user
        })
    }).then(response => {
        if(response.redirected){
            window.location.href = response.url;
        }else{
            return response;
        }
    }).then(response => response.json())


}