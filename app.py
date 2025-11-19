from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your-secret-key"

# In-memory user store (for demo only)
users = {}

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("signed_in"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.get(username)
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            return redirect(url_for("signed_in"))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users:
            return "User already exists", 400
        users[username] = {"password": generate_password_hash(password)}
        return redirect(url_for("login"))
    return render_template('signup.html')

@app.route("/signed-in")
def signed_in():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template('signedin.html', username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
