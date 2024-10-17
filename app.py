from flask import Flask, render_template,request, redirect,flash,url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db,User, Service, ServiceRequest, Review, Customer,Customer, Professional
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "1431983a28650982eb94507830943ee323bc97c0fb27f865c18cae6229e00e867a5981c0b970ac7b750a26892cf02f7f204d89a01b5cfcf4434ee7a420e7b7f5"

db.init_app(app)

with app.app_context():
    db.create_all()
 
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

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

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['user_role'] = "admin"
        return redirect(url_for("admin_dashboard"))

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid username','danger')
        return redirect(url_for("login"))
    if not check_password_hash(user.passhash,password):
        flash('Invalid password','danger')
        return redirect(url_for("login"))
    
    if user.role == 'professional':
        professional = Professional.query.filter_by(id=user.id).first()
        session['user_role'] = 'professional'
        session['user_id'] = user.id
        # session['service_id'] = professional.service_id
        return redirect(url_for("professional_dashboard"))
    else:
        customer = Customer.query.filter_by(id=user.id).first()
        session['user_role'] = 'customer'
        session['user_id'] = user.id
        return redirect(url_for("customer_dashboard"))

@app.route("/register")
def register():
    services = Service.query.all()
    return render_template("register.html", services=services)

@app.route("/register", methods=["POST"])
def register_post():

    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")
    confirm_password = request.form.get("confirm_password")
    role = request.form.get("role")
    pincode = request.form.get("pincode")
    address = request.form.get("address")

    flash(role,'success')
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
    id = int(uuid.uuid4().int >> 100)

    if role == 'professional':
        service_id = request.form.get("service_id")
        service_name = request.form.get("service_name")
        experience = request.form.get("experience")
        if not service_id:
            flash('Please select a service','danger')
            return redirect(url_for("register"))
        new_professional = Professional(id=id,service_name=service_name, service_id=service_id,address=address, pincode=pincode, experience=experience)
        new_user = User(id=id, username=username, passhash=password_hash, name=name, role=role)

        try:
            db.session.add(new_user)
            db.session.add(new_professional)
            db.session.commit()
            flash('professional user added successfully!','success')
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash('Error in registering user: ' + str(e) , 'danger')
    
    # for customer
    new_customer = Customer(id=id,address=address, pincode=pincode)
    new_user = User(id=id, username=username, passhash=password_hash, name=name, role=role)
    try:
        db.session.add(new_user)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for("login"))
    except Exception as e:
        db.session.rollback()
        flash('Error in registering user: ' + str(e) , 'danger')

    return redirect(url_for("register"))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_role' in session and session['user_role'] == 'admin':
        return render_template('admin_dashboard.html')  # Create this template
    else:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))

@app.route('/add_service', methods=['POST'])
def add_service():
    if 'user_role' in session and session['user_role'] == 'admin':
        service_name = request.form.get('service_name')
        service_description = request.form.get('service_description')
        base_price = float(request.form.get('base_price'))  # Convert to float
        time_required = int(request.form.get('time_required'))  # Convert to int
        service_id = int(uuid.uuid4().int >> 100)  # Create a unique service ID
        print(service_name, service_description, base_price, time_required, service_id)
        # Create a new service instance
        new_service = Service(id=service_id, time_required=time_required,
                              service_name=service_name, description=service_description,
                              price=base_price)
        db.session.add(new_service)

        try:
            db.session.commit()
            flash('Service added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding service: ' + str(e), 'danger')

        return redirect(url_for('admin_dashboard'))
    else:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('login'))

@app.route('/customer_dashboard')
def customer_dashboard():
    # Logic for the customer dashboard

    return render_template('customer_dashboard.html')

@app.route('/professional_dashboard')
def professional_dashboard():
    # Logic for the professional dashboard
    user_id = session['user_id']
    professional = Professional.query.all()
    service = Service.query.all()
    flash(session['user_id'],'success')
    flash(professional,'success')
    flash(service,'success')
    return render_template('professional_dashboard.html', professional=professional, service=service)

@app.route('/accept_service/<int:service_id>')
def accept_service(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        service.status = 'accepted'  # Change status as needed
        db.session.commit()
        flash('Service accepted!', 'success')
    else:
        flash('Service not found.', 'danger')
    return redirect(url_for('professional_dashboard'))

@app.route('/reject_service/<int:service_id>')
def reject_service(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        service.status = 'rejected'  # Change status as needed
        db.session.commit()
        flash('Service rejected!', 'danger')
    else:
        flash('Service not found.', 'danger')
    return redirect(url_for('professional_dashboard'))

@app.route('/profile')
def profile():
    # Implement profile viewing/editing logic here
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)
