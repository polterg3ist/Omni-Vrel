const themeSwitch = document.querySelector('.theme-switch_btn');
const theme = document.querySelector('body');

themeSwitch.addEventListener('click', SwitchTheme)

function SwitchTheme(){
    if (theme.style.backgroundColor === 'aliceblue') {
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
            location.reload();
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
            location.reload();
        })
    }
}