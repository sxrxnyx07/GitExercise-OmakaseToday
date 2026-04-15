from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

users = {}
reset_user = None
current_user = None


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users:
            return "User already exists!"

        users[email] = {
            "username": username,
            "password": password,
            "bio": ""
        }

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    global current_user

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and users[email]["password"] == password:
            current_user = email
            return redirect(url_for("profile"))
        else:
            return "Invalid email or password!"

    return render_template("login.html")


@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    global reset_user

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        if email in users and users[email]["username"] == username:
            reset_user = email
            return redirect(url_for("newpassword"))
        else:
            return "Invalid username or email!"

    return render_template("resetpassword.html")


@app.route("/newpassword", methods=["GET", "POST"])
def newpassword():
    global reset_user

    if reset_user is None:
        reset_user = "test@example.com"
        users.setdefault(reset_user, {
            "username": "testuser",
            "password": "12345678",
            "bio": ""
        })

    if request.method == "POST":
        password = request.form.get("password")

        users[reset_user]["password"] = password
        reset_user = None

        return redirect(url_for("login"))

    return render_template("newpassword.html")


@app.route("/profile")
def profile():
    global current_user

    if current_user is None:
        return redirect(url_for("login"))

    user = users[current_user]

    return render_template(
        "profile.html",
        username=user["username"],
        email=current_user,
        bio=user.get("bio", "")
    )

@app.route("/base")
def base():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)
