from flask import Flask, request, render_template,flash,redirect,url_for

from models import db, User, Service, ServiceRequest, Review

from app import app
from werkzeug.security import generate_password_hash


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")
    confirm_password = request.form.get("confirm_password")
    role = request.form.get("role")
    if not username or not password or not confirm_password or not role:
        flash('Please fill out all fields')
        return redirect(url_for("register"))
    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for("register"))
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists, Try Logging in')
        return redirect(url_for("register"))
    
    password_hash = generate_password_hash(password)

    new_user = User(username=username,passhash=password_hash,name=name,role=role,id=username)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
