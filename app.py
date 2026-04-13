from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
users = {}

# ✅ 新增（必须）
reset_user = None


@app.route("/")
def home():
    return render_template("home.html")



# ✅ REGISTER
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
            "password": password
        }

        return redirect(url_for("login"))

    return render_template("register.html")


# ✅ LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and users[email]["password"] == password:
            return redirect(url_for("profile"))
        else:
            return "Invalid email or password!"

    return render_template("login.html")


# ✅ PROFILE（你有用到）
@app.route("/profile")
def profile():
    return "Welcome to your profile 🎉"




# ✅ STEP 1：验证 username + email
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

    # ✅ TEST MODE: allow direct access
    if reset_user is None:
        reset_user = "test@example.com"
        users.setdefault(reset_user, {
            "username": "testuser",
            "password": "12345678"
        })

    if request.method == "POST":
        password = request.form.get("password")

        users[reset_user]["password"] = password
        reset_user = None

        return redirect(url_for("login"))

    return render_template("newpassword.html")



if __name__ == "__main__":
    app.run(debug=True)
