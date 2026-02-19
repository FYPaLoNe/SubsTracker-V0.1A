from flask import Flask, render_template, request, redirect
import json
from flask import session
import hashlib
import os



app = Flask(__name__)


app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- JSON işlemleri ----------
def load_subs():
    try:
        with open("subs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_subs(data):
    with open("subs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------- Ana sayfa ----------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    subs = load_subs()
    total = 0

    for sub in subs:
        price = float(sub.get("price", 0))
        sub_type = sub.get("type", "monthly")

        if sub_type == "monthly":
            total += price
        elif sub_type == "yearly":
            total += price / 12

    return render_template("index.html", subs=subs, total=round(total, 2))


# ---------- Abonelik ekleme ----------
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    price = float(request.form["price"])
    sub_type = request.form.get("type", "monthly")

    subs = load_subs()
    subs.append({
        "name": name,
        "price": price,
        "type": sub_type
    })
    save_subs(subs)

    return redirect("/")


# ---------- Abonelik silme ----------
@app.route("/delete/<int:index>")
def delete(index):
    subs = load_subs()
    if 0 <= index < len(subs):
        subs.pop(index)
        save_subs(subs)
    return redirect("/")


# ---------- Kullanıcılar ----------
def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_users(data):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        hashed = hash_password(password)

        for user in users:
            if user["username"] == username and user["password"] == hashed:
                session["user"] = username
                return redirect("/")

        return render_template("login.html", error="Hatalı kullanıcı adı veya şifre")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        # Aynı kullanıcı adı var mı?
        for user in users:
            if user["username"] == username:
                return render_template("register.html", error="Bu kullanıcı adı alınmış")

        users.append({
            "username": username,
            "password": hash_password(password)
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------- Çalıştır ----------
if __name__ == "__main__":
    app.run(debug=True)