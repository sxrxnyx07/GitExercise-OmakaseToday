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
// EMAIL CHECK (ONLY UI WARNING)
// =========================
if (page === "register" && email_input) {

    let timeout;

    email_input.addEventListener("input", () => {

        clearTimeout(timeout);

        timeout = setTimeout(async () => {

            const email = email_input.value.trim();

            if (!email) {
                emailExists = false;
                error_message.innerText = "";
                return;
            }

            const res = await fetch(`/check-email?email=${email}`);
            const data = await res.json();

            emailExists = data.exists;

            if (emailExists) {
                error_message.innerText = "⚠ This email is already registered";
                error_message.style.color = "red";
            } else {
                error_message.innerText = "";
            }

        }, 300);
    });
}

// =========================
// ONLY FRONTEND VALIDATION (NOT BLOCK SUBMIT)
// =========================
if (form) {
    form.addEventListener("submit", (e) => {

        let errors = [];

        if (!username_input.value) errors.push("Username required");
        if (!email_input.value) errors.push("Email required");
        if (!password_input.value) errors.push("Password required");

        if (password_input.value !== repeat_password_input.value) {
            errors.push("Passwords do not match");
        }

        if (errors.length > 0) {
            e.preventDefault();
            error_message.innerText = errors.join("\n");
        }
    });
}
function enableEdit() {
    const username = document.getElementById("username")
    const bio = document.getElementById("bio")
    const saveBtn = document.getElementById("saveBtn")

    if (username && bio) {
        username.disabled = false
        bio.disabled = false
    }

    if (saveBtn) {
        saveBtn.style.display = "inline-block"
    }
}

// =========================
// CLEAR STYLE
// =========================
document.querySelectorAll("input").forEach(input => {
    input.addEventListener("input", () => {
        input.parentElement.classList.remove("incorrect")
    })
})

const pages = [
    document.getElementById("s1"),
    document.getElementById("s2"),
    document.getElementById("s3")
]

let currentPage = 0;

function nextPage(){
    if (currentPage < pages.length){
        pages[currentPage].classList.add("flipped")
        currentPage++
    }
}

function prevPage(){
    if (currentPage > 0){
        currentPage--
        pages[currentPage].classList.remove("flipped")
    }
}
let autoFlip = setInterval(() => {

    if (currentPage < pages.length){
        nextPage()
    } else {
        // back to first page
        while(currentPage > 0){
            prevPage()
        }
    }

}, 10000)
function goLogin(){
    window.location.href = "/login"
}

function slideLeft() {
    document.getElementById("slider").scrollBy({
        left: -220,
        behavior: "smooth"
    });
}

function slideRight() {
    document.getElementById("slider").scrollBy({
        left: 220,
        behavior: "smooth"
    });
}
function showSidebar() {
    const sidebar = document.querySelector(".sidebar")
    if (sidebar) {
        sidebar.style.display = "flex"
    }
}

function hideSidebar() {
    const sidebar = document.querySelector(".sidebar")
    if (sidebar) {
        sidebar.style.display = "none"
    }
}
