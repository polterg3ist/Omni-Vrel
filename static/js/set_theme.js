// dark-mode media query matched or not
let matched = window.matchMedia('(prefers-color-scheme: dark)').matches;
console.log(matched)

if (matched) {
    fetch("/set_theme", {
    method: 'POST',
    credentials: 'same-origin',
    headers:{
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
        'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({'color': "black"})
    }).then(data => {
        location.reload()
    })
}
else{
    fetch("/set_theme", {
    method: 'POST',
    credentials: 'same-origin',
    headers:{
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
        'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({'color': "white"})
    }).then(data => {
        location.reload()
    })
}




