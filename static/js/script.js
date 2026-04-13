const form = document.getElementById('form')
const username_input = document.getElementById('username-input')
const email_input = document.getElementById('email-input')
const password_input = document.getElementById('password-input')
const repeat_password_input = document.getElementById('repeat-password-input')
const error_message = document.getElementById('error-message')

form.addEventListener('submit', (e) => {

    let errors = []

    // ✅ SIGNUP
    if (username_input && repeat_password_input) {
        errors = getSignupFormErrors(
            username_input.value,
            email_input.value,
            password_input.value,
            repeat_password_input.value
        )
    }

    // ✅ NEW PASSWORD
    else if (password_input && repeat_password_input) {
        errors = getResetPasswordErrors(
            password_input.value,
            repeat_password_input.value
        )
    }

    // ✅ LOGIN
    else {
        errors = getLoginFormErrors(
            email_input.value,
            password_input.value
        )
    }

    if (errors.length > 0) {
        e.preventDefault()
        error_message.innerText = errors.join(". ")
    }
})


// ✅ SIGNUP VALIDATION
function getSignupFormErrors(username, email, password, repeatpassword) {
    let errors = []

    if (!username) {
        errors.push('Username is required')
        username_input.parentElement.classList.add('incorrect')
    }
    if (!email) {
        errors.push('Email is required')
        email_input.parentElement.classList.add('incorrect')
    }
    if (!password) {
        errors.push('Password is required')
        password_input.parentElement.classList.add('incorrect')
    }
    if (password.length < 8) {
        errors.push('Password must have at least 8 characters')
        password_input.parentElement.classList.add('incorrect')
    }
    if (password !== repeatpassword) {
        errors.push('Password does not match repeated password')
        password_input.parentElement.classList.add('incorrect')
        repeat_password_input.parentElement.classList.add('incorrect')
    }

    return errors
}


// ✅ LOGIN VALIDATION
function getLoginFormErrors(email, password) {
    let errors = []

    if (!email) {
        errors.push('Email is required')
        email_input.parentElement.classList.add('incorrect')
    }
    if (!password) {
        errors.push('Password is required')
        password_input.parentElement.classList.add('incorrect')
    }
    if (password.length < 8) {
        errors.push('Password must have at least 8 characters')
        password_input.parentElement.classList.add('incorrect')
    }

    return errors
}


// ✅ RESET PASSWORD VALIDATION
function getResetPasswordErrors(password, repeatpassword) {
    let errors = []

    if (!password) {
        errors.push('Password is required')
        password_input.parentElement.classList.add('incorrect')
    }

    if (password.length < 8) {
        errors.push('Password must have at least 8 characters')
        password_input.parentElement.classList.add('incorrect')
    }

    if (password !== repeatpassword) {
        errors.push('Passwords do not match')
        password_input.parentElement.classList.add('incorrect')
        repeat_password_input.parentElement.classList.add('incorrect')
    }

    return errors
}


// ✅ REMOVE ERROR STYLE
const allInputs = [username_input, email_input, password_input, repeat_password_input].filter(input => input != null)

allInputs.forEach(input => {
    input.addEventListener('input', () => {
        if (input.parentElement.classList.contains('incorrect')) {
            input.parentElement.classList.remove('incorrect')
            error_message.innerText = ''
        }
    })
})
