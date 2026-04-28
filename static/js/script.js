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
    form.addEventListener("submit", (e) => {

        let errors = [];

        // REGISTER
        if (page === "register") {
            if (!username_input?.value) errors.push("Username required");
            if (!email_input?.value) errors.push("Email required");
            if (!password_input?.value) errors.push("Password required");

            if (password_input?.value !== repeat_password_input?.value) {
                errors.push("Passwords do not match");
            }
        }

        // RESET
        else if (page === "reset") {
            if (!email_input?.value) errors.push("Email required");
        }

        // NEW PASSWORD
        else if (page === "newpassword") {
            if (!password_input?.value) errors.push("Password required");

            if (password_input?.value !== repeat_password_input?.value) {
                errors.push("Passwords do not match");
            }
        }

        // LOGIN
        else if (page === "login") {
            if (!email_input?.value) errors.push("Email required");
            if (!password_input?.value) errors.push("Password required");
        }

        if (errors.length > 0) {
            e.preventDefault();
            error_message.innerText = errors.join("\n");
        }
    });
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
// =========================
// SEARCH FUNCTION
// =========================
function filterRecipes() {
    const input = document.getElementById("recipeSearch").value.toLowerCase();
    const rows = document.querySelectorAll("#recipeBody tr");

    rows.forEach(row => {
        const nameInput = row.querySelector("input[name='name']");
        if (!nameInput) return;

        const name = nameInput.value.toLowerCase();

        if (name.includes(input)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}
const recipeSearchInput = document.getElementById("recipeSearch");

if (recipeSearchInput) {
    recipeSearchInput.addEventListener("input", filterRecipes);
}

function filterUsers() {
    const input = document.getElementById("userSearch").value.toLowerCase();
    const rows = document.querySelectorAll("#userBody tr");

    rows.forEach(row => {
        const cells = row.querySelectorAll("td");

        if (cells.length < 2) return;

        const email = cells[1].textContent.toLowerCase();

        if (email.includes(input)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}
const userSearchInput = document.getElementById("userSearch");
if (userSearchInput) {
    userSearchInput.addEventListener("input", filterUsers);
}

async function toggleSave(button) {

    const recipeId = button.dataset.id;
    const isSaved = button.classList.contains("saved");

    button.disabled = true;

    const url = isSaved
        ? `/unsave-recipe/${recipeId}`
        : `/save-recipe/${recipeId}`;

    const res = await fetch(url);

    if (!res.ok) return;
    location.reload();

    button.classList.toggle("saved");

    const savedGrid = document.getElementById("savedGrid");
    const emptyState = document.getElementById("emptyState");

    // =========================
    // SAVE ACTION
    // =========================
    if (!isSaved) {

        // remove empty state
        if (emptyState) emptyState.remove();

        // create new card (you can enhance styling later)
        const card = document.createElement("div");
        card.className = "ritual-card";
        card.id = `card-${recipeId}`;

        card.innerHTML = `
            <img src="${button.dataset.image}">
            <h3>${button.dataset.name}</h3>
        `;

        savedGrid.appendChild(card);
    }

    // =========================
    // UNSAVE ACTION
    // =========================
    else {

        const card = document.getElementById(`card-${recipeId}`);
        if (card) card.remove();

        // if empty → show empty state again
        if (savedGrid.children.length === 0) {

            const empty = document.createElement("div");
            empty.className = "empty-wrapper";
            empty.id = "emptyState";

            empty.innerHTML = `
                <div class="empty-state-card">
                    <div class="empty-icon">🍽️</div>
                    <h2>No Saved Rituals Yet</h2>
                    <p>Start exploring delicious recipes and build your collection.</p>
                    <a href="/" class="explore-btn">Explore Recipes</a>
                </div>
            `;

            savedGrid.appendChild(empty);
        }
    }

    button.disabled = false;
}
function enableEditRow(btn) {
    const row = btn.closest("tr");

    // hide text
    row.querySelectorAll(".view").forEach(el => el.style.display = "none");

    // show inputs
    row.querySelectorAll(".edit").forEach(el => el.hidden = false);

    // toggle buttons
    btn.style.display = "none";
    row.querySelector(".save-btn").hidden = false;
}
function openAddModal() {

    document.getElementById("editModal").style.display = "block";
    document.getElementById("editForm").action = "/admin/recipes/add";
    document.querySelector(".modal-content h2").innerText = "Add New Recipe";
    // clear all fields
    document.getElementById("edit-name").value = "";
    document.getElementById("edit-rating").value = "";
    document.getElementById("edit-clean").value = "";
    document.getElementById("edit-full").value = "";
    document.getElementById("edit-directions").value = "";
    document.getElementById("edit-timing").value = "";
    document.getElementById("edit-category").value = "";
    document.getElementById("edit-flavor").value = "";
    const preview = document.getElementById("imagePreview");
    if (preview) {
        preview.src = "";
        preview.style.display = "none";
    }
}

function openEditModal(id, name, rating, clean, full, directions, timing, category, flavor) {

    document.getElementById("editModal").style.display = "block";
    document.getElementById("editForm").action = `/admin/recipes/update/${id}`;
    document.querySelector(".modal-content h2").innerText = "Edit Recipe";
    document.getElementById("edit-mode").value = "edit";
    document.getElementById("edit-name").value = name;
    document.getElementById("edit-rating").value = rating;
    document.getElementById("edit-clean").value = clean;
    document.getElementById("edit-full").value = full;
    document.getElementById("edit-directions").value = directions;
    document.getElementById("edit-timing").value = timing;
    document.getElementById("edit-category").value = category;
    document.getElementById("edit-flavor").value = flavor;
}


function closeModal() {
    document.getElementById("editModal").style.display = "none";
}

// 点击外面关闭
window.onclick = function(event) {
    const modal = document.getElementById("editModal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
document.addEventListener("DOMContentLoaded", function () {

    const imageInput = document.getElementById("imageInput");
    const preview = document.getElementById("imagePreview");

    if (imageInput) {
        imageInput.addEventListener("change", function () {

            const file = this.files[0];

            if (file) {
                const reader = new FileReader();

                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = "block";
                };

                reader.readAsDataURL(file);
            }
        });
    }

});
function openTab(tabName) {

    // hide all tabs
    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // remove active button
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    // show selected tab
    document.getElementById("tab-" + tabName).classList.add("active");

    // highlight button
    event.target.classList.add("active");
}
function filterSavedRecipes() {
    const input = document.getElementById("savedSearch").value.toLowerCase();
    const cards = document.querySelectorAll(".recipe-card");

    cards.forEach(card => {
        const title = card.querySelector(".recipe-title").innerText.toLowerCase();

        if (title.includes(input)) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// live search
const savedSearchInput = document.getElementById("savedSearch");
if (savedSearchInput) {
    savedSearchInput.addEventListener("input", filterSavedRecipes);
}
const grid = document.querySelector(".saved-grid");

let visibleCount = 0;

cards.forEach(card => {
    const title = card.querySelector(".recipe-title").innerText.toLowerCase();

    if (title.includes(input)) {
        card.style.display = "block";
        visibleCount++;
    } else {
        card.style.display = "none";
    }
});

if (visibleCount === 0) {
    grid.innerHTML = "<p style='text-align:center;'>No matching recipes 😢</p>";
}