const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.querySelector('.container');

signUpButton.addEventListener('click', () => {
    container.classList.add('right-panel-active');
});

signInButton.addEventListener('click', () => {
    container.classList.remove('right-panel-active');
});

const togglePasswordButtons = document.querySelectorAll('.toggle-password');

togglePasswordButtons.forEach(button => {
    button.addEventListener('click', () => {
        const passwordInput = button.previousElementSibling;
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            button.textContent = 'Hide';
        } else {
            passwordInput.type = 'password';
            button.textContent = 'Show';
        }
    });
});

const passwordInput = document.getElementById('psw');
const c_passwordInput = document.getElementById('confirm-psw');
const passwordRules = {
    length: document.getElementById('length'),
    uppercase: document.getElementById('uppercase'),
    lowercase: document.getElementById('lowercase'),
    number: document.getElementById('number'),
    special: document.getElementById('special')
};

passwordInput.addEventListener('input', () => {
    const value = passwordInput.value;

    passwordRules.length.classList.toggle('valid', value.length >= 8);
    passwordRules.length.classList.toggle('invalid', value.length < 8);

    passwordRules.uppercase.classList.toggle('valid', /[A-Z]/.test(value));
    passwordRules.uppercase.classList.toggle('invalid', !/[A-Z]/.test(value));

    passwordRules.lowercase.classList.toggle('valid', /[a-z]/.test(value));
    passwordRules.lowercase.classList.toggle('invalid', !/[a-z]/.test(value));

    passwordRules.number.classList.toggle('valid', /\d/.test(value));
    passwordRules.number.classList.toggle('invalid', !/\d/.test(value));
});