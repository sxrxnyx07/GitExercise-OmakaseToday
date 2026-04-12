
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
users = {}
@app.route("/")
def home():
    return redirect(url_for("login"))

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

        print("Current users:", users)

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email in users and users[email]["password"] == password:
            return f"Welcome {users[email]['username']}! 🎉"
        else:
            return "Invalid email or password!"

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
