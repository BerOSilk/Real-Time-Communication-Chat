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


function load_chat(target,request){
    const name = document.getElementById('user').textContent;
    const url = `/render?name=${name}&request=${request}-chat&target=${target}`;

    fetch(url)
    .then(response => response.text())
    .then(data => {
        const mc = document.getElementById('messages-container')
        mc.innerHTML = data
    });
}

function load_profile(target,request){
    const url = `/render?request=${request}-profile&target=${target}`;

    fetch(url)
    .then(response => response.text())
    .then(data => {
        const upc = document.getElementById('user-profile-container')
        upc.style.visibility = 'visible';
        upc.innerHTML = data
    });
}

function load(target,request){
    load_profile(target,request)
    load_chat(target,request)
}


function send_message(){

    user = document.getElementById('user').textContent;

    message = document.createElement('div');
    message.className = 'message';
    img = document.createElement('img');
    img.className = 'profile-pic';
    img.alt = 'pfp';
    img.src = document.getElementById('user-pfp').src
    message_content = document.createElement('div');
    message_content.className = 'message-content';
    message_header = document.createElement('div');
    message_header.className ='message-header';
    person = document.createElement('span');
    person.className = 'person';
    person.textContent = user;
    timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    text = document.createElement('div');
    text.className ='text';


    message_header.appendChild(person);
    message_header.appendChild(timestamp);

    message_content.appendChild(message_header);
    message_content.appendChild(text);
    
    message.appendChild(img);
    message.appendChild(message_content);

    chat_input = document.getElementById('chat-message-input')

    text.textContent = chat_input.value;
    


    sent_to = document.querySelector('.user-info-container h1').textContent;

    url = `/send?name=${user}&msg=${chat_input.value}&to=${sent_to}`;

    fetch('/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: user,
            msg: chat_input.value,
            to: sent_to
        })
    })
    .then(response => response.json())
    .then(data => {
        timestamp.textContent = data.time;
    })

    document.getElementById('messages-container').appendChild(message);

    chat_input.value = '';
}