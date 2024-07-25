document.addEventListener('DOMContentLoaded',()=>{
    const pfp = document.getElementById("profile-picture");
    uploaded_img = ''
    pfp.addEventListener('change', () => {
        const reader = new FileReader();
        const pfp_img = document.getElementById('pfp-img');
        reader.addEventListener('load', () => {
            uploaded_img = reader.result;
            pfp_img.src = uploaded_img
        });
        reader.readAsDataURL(pfp.files[0]);
    });

    const update_button = document.getElementById('update-button');
    const sub_conatiner = document.getElementById('sub-container');
    update_button.addEventListener('click', () => {
        if(update_button.innerHTML == 'Update →'){
            update_button.innerHTML = 'Cancel';
            sub_conatiner.style.visibility = "visible";
            fetch('/update',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    button: update_button.innerHTML
                })
            })
            .then(response  => response.text())
            .then(data => {
                sub_conatiner.innerHTML = data
            })
            
        }else{
            update_button.innerHTML = 'Update →';
            sub_conatiner.style.visibility = "hidden";
            sub_conatiner.innerHTML = '';
        }
    });


});


function change(argument){
    fetch('/update',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user: document.getElementById('username').value,
            button: argument,
            old_psw: document.getElementById('old-psw-input').value,
            new_psw: document.getElementById('new-psw-input').value,
            confirm_psw: document.getElementById('confirm-psw-input').value
        })
    })
    .then(response => response.json())
    .then(data => {
        let msg = data.message;
        if (msg == 'Incorrect password'){
            document.getElementById('old-psw-error').innerHTML = msg;
        }else if(msg == 'Password must contain at least 8 characters, including uppercase, lowercase, and numbers'){
            document.getElementById('new-psw-error').innerHTML = msg;
        }else if(msg == 'Passwords do not match'){
            document.getElementById('confirm-psw-error').innerHTML = msg;
        }else{
            console.log(msg);
            document.getElementById('updated').innerHTML = 'updated, save to apply';
            document.getElementById('updated-new-psw').value = msg;
            document.getElementById('sub-container').style.visibility = 'hidden';
            document.getElementById('sub-container').innerHTML = '';
            document.getElementById('update-button').innerHTML = 'Update →';
        }
    })
}

document.getElementById('inputField').addEventListener('input', function () {
    const input = this.value.toLowerCase();
    const dropdownList = document.getElementById('dropdownList');

    const suggestions = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry', 'Fig', 'Grape', 'Honeydew'];

    const filteredSuggestions = suggestions.filter(item => item.toLowerCase().includes(input));

    dropdownList.innerHTML = '';

    if (filteredSuggestions.length > 0 && input.length > 0) {
        filteredSuggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            li.addEventListener('click', function () {
                document.getElementById('inputField').value = suggestion;
                dropdownList.classList.add('hidden');
            });
            dropdownList.appendChild(li);
        });
        dropdownList.classList.remove('hidden');
    } else {
        dropdownList.classList.add('hidden');
    }
});

document.addEventListener('click', function (event) {
    const dropdownList = document.getElementById('dropdownList');
    if (!event.target.closest('.input-container')) {
        dropdownList.classList.add('hidden');
    }
});