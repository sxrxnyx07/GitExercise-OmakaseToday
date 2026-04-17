const page = document.body.dataset.page || ""

const form = document.getElementById('form')
const username_input = document.getElementById('username-input')
const email_input = document.getElementById('email-input')
const password_input = document.getElementById('password-input')
const repeat_password_input = document.getElementById('repeat-password-input')
const error_message = document.getElementById('error-message')

let emailExists = false

// =========================
// SUBMIT
// =========================
if (form) {
    form.addEventListener('submit', (e) => {

        let errors = []

        if (page === "register") {
            errors = getSignupFormErrors(
                username_input?.value,
                email_input?.value,
                password_input?.value,
                repeat_password_input?.value,
                emailExists
            )
        }

        else if (page === "reset") {
            errors = getResetErrors(
                username_input?.value,
                email_input?.value
            )
        }

        else if (page === "newpassword") {
            errors = getNewPasswordErrors(
                password_input?.value,
                repeat_password_input?.value
            )
        }

        else if (page === "login") {
            errors = getLoginFormErrors(
                email_input?.value,
                password_input?.value
            )
        }

        if (errors.length > 0) {
            e.preventDefault()
            error_message.innerText = errors.join("\n")
        }
    })
}

// =========================
// RESET STEP 1
// =========================
function getResetErrors(username, email) {
    let errors = []

    if (!username) errors.push("Username is required")
    if (!email) errors.push("Email is required")

    return errors
}

// =========================
// NEW PASSWORD
// =========================
function getNewPasswordErrors(password, repeat) {
    let errors = []

    if (!password) errors.push("Password is required")
    if (password && password.length < 8)
        errors.push("Password must be at least 8 characters")

    if (password !== repeat)
        errors.push("Passwords do not match")

    return errors
}

// =========================
// LOGIN
// =========================
function getLoginFormErrors(email, password) {
    let errors = []

    if (!email) errors.push("Email is required")
    if (!password) errors.push("Password is required")

    return errors
}

// =========================
// REGISTER
// =========================
function getSignupFormErrors(username, email, password, repeat, emailExists) {
    let errors = []

    if (!username) errors.push("Username is required")
    if (!email) errors.push("Email is required")
    if (emailExists) errors.push("This email is already registered!")
    if (!password) errors.push("Password is required")
    if (password !== repeat) errors.push("Passwords do not match")

    return errors
}

// =========================
// EMAIL CHECK REGISTER ONLY
// =========================
if (page === "register" && email_input) {

    let timeout

    email_input.addEventListener('input', () => {

        clearTimeout(timeout)

        timeout = setTimeout(async () => {

            const email = email_input.value.trim()

            if (!email) {
                emailExists = false
                return
            }

            const res = await fetch(`/check-email?email=${email}`)
            const data = await res.json()

            emailExists = data.exists

            if (emailExists) {
                error_message.innerText = "This email is already registered!"
            } else {
                if (error_message.innerText === "This email is already registered!") {
                    error_message.innerText = ""
                }
            }

        }, 300)
    })
}

// =========================
// CLEAR STYLE
// =========================
document.querySelectorAll("input").forEach(input => {
    input.addEventListener("input", () => {
        input.parentElement.classList.remove("incorrect")
    })
})






