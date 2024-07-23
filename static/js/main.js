
function fetchData(value){

    const name = document.getElementById('user').textContent;
    const url = `/render?value=${encodeURIComponent(value)}&name=${name}`

    fetch(url)
        .then(response => response.text())
        .then(data => {
            console.log(data)
            document.getElementById('users-container').innerHTML = data;
        });
}


document.addEventListener('DOMContentLoaded',()=>{
    const search = document.getElementById("user-search");
    search.addEventListener('input', () => {
        fetchData(search.value);
    });
});
