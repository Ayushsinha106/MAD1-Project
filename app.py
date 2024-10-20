from flask import Flask, render_template,request, redirect,flash,url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db,User, Service, ServiceRequest, Review, Customer,Customer, Professional
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, datetime
from sqlalchemy.orm import joinedload

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
    print("login 1")

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
        print("login as customer")
        customer = Customer.query.filter_by(id=user.id).first()
        session['user_role'] = 'customer'
        session['user_id'] = user.id
        return redirect(url_for("customer_dashboard"))

@app.route("/register")
def register():
    services =  db.session.query(Service.service_name).distinct().all()

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
    contact = request.form.get("contact")

    print(role=='professional',role,"role")
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
        # service_id = request.form.get("service_id")
        service_name = request.form.get("service_name")
        experience = request.form.get("experience")
        description = request.form.get("description")
        print(service_name, experience,description)
        if not service_name:
            flash('Please select a service','danger')
            return redirect(url_for("register"))
        new_professional = Professional(id=id, service_name=service_name,address=address, pincode=pincode, experience=experience,description=description,contact=contact)
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
    new_customer = Customer(id=id,address=address, pincode=pincode,contact=contact)
    new_user = User(id=id, username=username, passhash=password_hash, name=name, role=role)
    try:
        db.session.add(new_user)
        db.session.add(new_customer)
        db.session.commit()
        flash('customer user added successfully!','success')
        return redirect(url_for("login"))
    except Exception as e:
        db.session.rollback()
        flash('Error in registering user: ' + str(e) , 'danger')

    return redirect(url_for("register"))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_role' in session and session['user_role'] == 'admin':
        services = Service.query.all()
        professionals = Professional.query.all()
        customers = Customer.query.all()
        service_requests = ServiceRequest.query.all()
        print(services,professionals,customers,service_requests, 'services,professionals,customers,service_requests')
        return render_template('admin_dashboard.html',customers=customers,professionals=professionals,services=services,service_requests=service_requests)  # Create this template
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

@app.route('/update_service', methods=['POST'])
def update_service():
    service_id = request.form.get('service_id')
    service = Service.query.get_or_404(service_id)
    service_name = request.form.get('service_name')
    description = request.form.get('description')
    price = request.form.get('price')
    Time_required = request.form.get('TimeRequired')

    if not service_name or not description or not price or not Time_required:
        flash('All fields are required', 'danger')
        return redirect(url_for('services'))

    try:
        service.service_name = service_name
        service.description = description
        service.price = float(price)
        service.time_required = int(Time_required)
        db.session.commit()
        flash('Service updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating service: {str(e)}', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    print(service, 'service')
    if service:
        try:
            ServiceRequest.query.filter_by(service_id=service_id).delete()

            db.session.delete(service)
            db.session.commit()
            flash('Service deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting service: ' + str(e), 'danger')
    else:
        flash('Service not found.', 'warning')
    
    return redirect(url_for('admin_dashboard'))  # Redirect to the desired page after deletion

@app.route('/delete_professional/<int:professional_id>', methods=['POST'])
def delete_professional(professional_id):
    professional = Professional.query.filter_by(id=professional_id).first()
    if professional:
        try:
            User.query.filter_by(id=professional_id).delete()

            ServiceRequest.query.filter_by(professional_id=professional_id).update(
                {
                    'professional_id': None,
                    'status': 'requested'
                }
            )

            db.session.delete(professional)
            db.session.commit()
            flash('Professional deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting service: ' + str(e), 'danger')
    else:
        flash('Service not found.', 'warning')
    
    return redirect(url_for('admin_dashboard'))  # Redirect to the desired page after deletion

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id).first()
    if customer:
        try:
            User.query.filter_by(id=customer_id).delete()
            ServiceRequest.query.filter_by(customer_id=customer_id).delete()

            db.session.delete(customer)
            db.session.commit()
            flash('Customer deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting service: ' + str(e), 'danger')
    else:
        flash('Service not found.', 'warning')
    
    return redirect(url_for('admin_dashboard'))  # Redirect to the desired page after deletion


@app.route('/customer_dashboard')
def customer_dashboard():
    # Logic for the customer dashboard
    user_id = session['user_id']
    customer = Customer.query.get(user_id)
    services =  db.session.query(Service.service_name).distinct().all()

    user = User.query.get(user_id)
    service_requests = ServiceRequest.query.filter_by(customer_id=user_id).all()
    
    return render_template('customer_dashboard.html',service_requests=service_requests,user=user, customer=customer, services=services)

@app.route('/select-service', methods=['POST'])
def select_service():
    service_name = request.form.get('service_name')

    if not service_name:
        flash('Please select a service', 'danger')
        return redirect(url_for('customer_dashboard'))

    # Query packages related to the selected service ID
    packages = Service.query.filter_by(service_name=service_name).all()
    print(packages, 'packages')

    user_id = session['user_id']
    # Get the list of all services to display in the dropdown
    services = db.session.query(Service.service_name).distinct().all()
    customer = Customer.query.get(user_id)
    user = User.query.get(user_id)
    service_requests = ServiceRequest.query.filter_by(customer_id=user_id).all()


    # Render the customer dashboard template with the available packages
    return render_template('customer_dashboard.html', services=services, packages=packages,customer=customer,user=user,service_requests=service_requests)

@app.route('/edit_service_request/<int:request_id>', methods=['POST'])
def edit_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    print(service_request.professional_id, 'service_request.professional_id')
    service_request.status = request.form.get('status')
    if service_request.status == 'closed' and service_request.professional_id == None:
        service_request.rating = None
        service_request.remarks = None
    else:
        service_request.remarks = request.form.get('remarks')
        service_request.rating = request.form.get('rating')
        professional = Professional.query.get(service_request.professional_id)
        print(professional.service_id, 'professional.service_id')
        professional.service_id = None
        print(professional.service_id, 'professional.service_id')
    # If the status is 'accepted' and the customer is closing the request
    print(service_request.professional_id, 'service_request.professional_id')
    try:
        db.session.commit()
        flash('Service request updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating service request: {e}', 'danger')

    return redirect(url_for('customer_dashboard'))

@app.route('/book-service/<int:package_id>', methods=['POST'])
def book_service(package_id):
    # Get the logged-in user's ID from the session
    print(package_id, 'package_id')
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to book a service.', 'danger')
        return redirect(url_for('login'))

    # Query the customer from the User and Customer tables using the user ID
    user = User.query.get(user_id)
    customer = Customer.query.get(user_id)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customer_dashboard'))

    # Query the selected package by its ID
    # package = Servive <------
    package = Service.query.get(package_id)
    if not package:
        flash('Selected package not found.', 'danger')
        return redirect(url_for('customer_dashboard'))

    # Get the professional offering the service (assuming each package is tied to a professional)
    packages = Service.query.filter_by(service_name=package_id).all()

    # Create a new service request
    service_request_id = int(uuid.uuid4().int >> 100)
    new_service_request = ServiceRequest(
        id=service_request_id,
        customer_id=customer.id,
        service_id=package.id,
        date_of_request=datetime.datetime.utcnow(),
        status='requested'
    )

    # Add the new service request to the database
    try:
        db.session.add(new_service_request)
        db.session.commit()
        flash('Service booked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error booking service: {str(e)}', 'danger')

    service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    services = db.session.query(Service.service_name).distinct().all()

    return redirect(url_for('customer_dashboard'))
    # return render_template('customer_dashboard.html', services=services, user=user,customer=customer,packages=packages,service_requests=service_requests)

@app.route('/professional_dashboard')
def professional_dashboard():
    # Logic for the professional dashboard
    user_id = session['user_id']
    professional = Professional.query.get(user_id)
    user = User.query.get(user_id)
    service = Service.query.all()
    accepted_services = ServiceRequest.query.filter_by(professional_id=user_id).all()
    today_services = (
    db.session.query(ServiceRequest)
    .join(Service)
    .filter(Service.service_name == professional.service_name)
    .filter(ServiceRequest.status == 'requested')
    .filter(ServiceRequest.rejected_by == [])
    .all()
)
    closed_services = (
    db.session.query(ServiceRequest)
    .join(Service)
    .filter(Service.service_name == professional.service_name)
    .filter(ServiceRequest.status == 'closed')
    .all()
)
    print(today_services, 'today_services')
    print(professional.address,service)
    return render_template('professional_dashboard.html',accepted_services=accepted_services,today_services=today_services, closed_services=closed_services,professional=professional, service=service,user=user)

@app.route('/accept_service/<int:service_id>')
def accept_service(service_id):
    service_request = ServiceRequest.query.get(service_id)
    professional = Professional.query.get(session['user_id'])
    print(professional, 'professional')
    if service_request:
        if service_request.status == 'accepted':
            flash('This service is already accepted byt Someone', 'danger')  # Change status as needed
            return redirect(url_for('professional_dashboard'))
        service_request.professional_id = session['user_id']
        professional.service_id = service_request.service_id
        service_request.status = 'accepted'
        db.session.commit()
        flash('Service accepted!', 'success')
    else:
        flash('Service not found.', 'danger')
    return redirect(url_for('professional_dashboard'))

@app.route('/reject_service/<int:service_id>')
def reject_service(service_id):
    print(service_id, 'service_id')
    professional_id = session['user_id']
    service_request = ServiceRequest.query.get_or_404(service_id)

    # Check if the professional has already rejected this service
    if professional_id in service_request.rejected_by:
        flash('You have already rejected this service', 'warning')
    else:
        # Add the professional's ID to the rejected_by list
        service_request.rejected_by.append(professional_id)
        db.session.commit()
        flash('Service request has been successfully rejected', 'success')

    return redirect(url_for('professional_dashboard'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    customers = Customer.query.all()
    professionals = Professional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    return render_template('search.html', customers=customers, professionals=professionals, services=services, service_requests=service_requests)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        if session.get("role") == "admin":
            # Admin search logic (e.g., by serviceRequest, customer, professional)
            service_requests = ServiceRequest.query.filter(ServiceRequest.name.contains(search_term)).all()
            customers = Customer.query.filter(Customer.name.contains(search_term)).all()
            professionals = Professional.query.filter(Professional.name.contains(search_term)).all()
            return render_template('search.html', role='admin', service_requests=service_requests, customers=customers, professionals=professionals)
        
        elif session.get("role") == "customer":
            # Customer search logic (e.g., by service)
            services = Service.query.filter(Service.name.contains(search_term)).all()
            return render_template('search.html', role='customer', services=services)
        
        elif session.get("role") == "professional":
            # Professional search logic (e.g., by date, pincode)
            service_requests = ServiceRequest.query.filter(
                (ServiceRequest.date.contains(search_term)) | 
                (ServiceRequest.pincode.contains(search_term))
            ).all()
            return render_template('search.html', role='professional', service_requests=service_requests)

    return render_template('search.html', role=session.get("role"))


@app.route('/profile')
def profile():
    # Implement profile viewing/editing logic here
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
