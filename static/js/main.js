function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight

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

    const logout = document.getElementById('logout-btn')
    logout.addEventListener('click', () => {
        let user = document.getElementById('user').textContent
    
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
        })
    })


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
    
    sleep(100).then(() => {
        const url2 = `/render?name=${name}&request=${request}-id&target=${target}`;
    
        fetch(url2)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                for(let i in data.id){
                    let tgt = document.getElementById(`message${data.id[i][0]}`)
                    
                    tgt.addEventListener("mouseleave",(event) =>{
                        document.getElementById(data.id[i][0]).style.visibility = "hidden";
                    })
                    
                    
                    tgt.addEventListener("mouseenter",(event) =>{
                        if(tgt.contains(event.target)){
                            document.getElementById(data.id[i][0]).style.visibility = "visible";
                        }
                    })

                    
                }
            })
            .catch(error => {
                console.error('There was a problem loading chat:', error);
            });
    })

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

    const new_msg = document.getElementById('new-msg')
    if(new_msg){
        new_msg.remove()
    }

    load_profile(target, request);
    load_chat(target, request);

    const ac = document.getElementById("actions-container");
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
        let active_chat = document.getElementById(data.target);
        if(active_chat.className.indexOf('active-user') != -1){
            let pfp_src = active_chat.querySelector('.pfp').src;
            const message = createMessageElement(data.header, data.message, data.time_now, pfp_src);
            document.getElementById('messages-container').appendChild(message);
            document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight;
        }else{
            let new_message = document.getElementById('new-msg');
            if(new_message){
                let value = new_message.textContent;
                new_message.textContent = Number(value) + 1;
            }else{
                new_message = document.createElement('div');
                new_message.id = 'new-msg';
                new_message.textContent = '1';
                active_chat.append(new_message);
            }            
        }
        var audio = new Audio('/static/audios/notification.wav');
        audio.play();
    }
});

function send_message(req) {

    const chatInput = document.getElementById('chat-message-input');
    const user = document.getElementById('user').textContent;
    const sentTo = document.querySelector('.user-info-container h1').textContent;

    const ac = document.getElementById('actions-container');

    if(ac.textContent.indexOf("Replying") != -1){
        let header = user
        header += " Replied to ";
        if(ac.textContent.indexOf("yourself") != -1) header += "himself";
        else header += sentTo;
        const message = createMessageElement(header,chatInput.value,'',document.getElementById('user-pfp').src);
        document.getElementById('messages-container').appendChild(message);
        

    
        fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                request: 'reply',
                name: user,
                msg: chatInput.value,
                to: sentTo,
                id: document.querySelector("#actions-container button").className
            })
        })
        .then(response => response.json())
        .then(data => {
            message.querySelector('.timestamp').textContent = data.time;
        })
        .catch(error => {
            console.error('Error sending message:', error);
        });
        
        io().emit('request_data', {to_user: sentTo, msg: chatInput.value, from_user: user, header: header });

        ac.innerHTML = "";
        ac.style.height = "0px";

    }else{
        const message = createMessageElement(user, chatInput.value, '',document.getElementById('user-pfp').src);

        document.getElementById('messages-container').appendChild(message);
    
        fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                request: 'send',
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
    
        io().emit('request_data', {to_user: sentTo, msg: chatInput.value, from_user: user, header: user });
    }
    chatInput.value = '';
    document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight
}

io().on('login_request', (data) => {
    // alert(data.status)
    let user_side = document.getElementById(data.user);
    if(user_side){
        let status = user_side.querySelector('.status');
        if(status){
            status.style.backgroundColor = data.status
        }
    }
})

io().on('logout_request', (data) =>{
    // alert(data.user)
    let user_side = document.getElementById(data.user);
    if(user_side){
        let status = user_side.querySelector('.status');
        if(status){
            status.style.backgroundColor = 'gray';
        }
    }
})



function reply(id){

    const ac = document.getElementById("actions-container");
    ac.style.height = "20px";
    

    const cancel = document.createElement("button");
    cancel.textContent = "cancel";
    cancel.type = "button";
    cancel.style.width = "50px";
    cancel.className = `${id}`;
    
    cancel.addEventListener("mouseenter", (event) => {
        event.target.style.background = "none";
        event.target.style.textDecoration = "underline";
    })

    cancel.addEventListener("mouseout", (event) => {
        event.target.style.textDecoration = "none";
    })

    cancel.addEventListener("click", () => {
        ac.innerHTML = "";
        ac.style.height = "0";
    })

    username = document.getElementById('user').textContent;
    reply_to = document.querySelector(`#message${id} .message-content .message-header .person`).textContent;

    let text = "";

    if(username === reply_to){
        text = " Replying to yourself";
    }else{
        text = ` Replying to ${reply_to}`;
    }

    ac.innerHTML = text;
    ac.appendChild(cancel);

    // send_message(text);

}