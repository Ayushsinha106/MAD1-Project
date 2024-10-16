from flask import Flask, render_template,request, redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from models import db,User, Service, ServiceRequest, Review
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)

import config

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "1431983a28650982eb94507830943ee323bc97c0fb27f865c18cae6229e00e867a5981c0b970ac7b750a26892cf02f7f204d89a01b5cfcf4434ee7a420e7b7f5"

db.init_app(app)

with app.app_context():
    db.create_all()
 

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid username','danger')
        return redirect(url_for("login"))
    if not check_password_hash(user.passhash,password):
        flash('Invalid password','danger')
        return redirect(url_for("login"))
    
    return redirect(url_for("index"))

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
        flash('Please fill out all fields','danger')
        return redirect(url_for("register"))
    if password != confirm_password:
        flash('Passwords do not match','danger')
        return redirect(url_for("register"))
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists.', 'success')
        return redirect(url_for("register"))
    
    password_hash = generate_password_hash(password)
    id = int(uuid.uuid4().int >> 64)
    new_user = User(username=username,passhash=password_hash,name=name,role=role,id=id)
    try:
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    except Exception as e:
        db.session.rollback()
        flash('Error in registering user: ' + str(e) , 'danger')


if __name__ == '__main__':
    app.run(debug=True)
