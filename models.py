from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passhash = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # Define relationships with Customer and Professional
    professional = db.relationship('Professional', backref='user', lazy=True)
    customer = db.relationship('Customer', backref='user', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    contact = db.Column(db.String(10), nullable=False)

    # Define relationship with ServiceRequest
    service_requests = db.relationship('ServiceRequest', back_populates='customer', lazy=True)

class Professional(db.Model):
    __tablename__ = 'professional'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    # service_name = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(10), nullable=False)
    experience = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    service_name = db.Column(db.Text(80),db.ForeignKey('service.service_name'), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(6), nullable=False)

    # Define relationship with ServiceRequest
    service_requests = db.relationship('ServiceRequest', back_populates='professional', lazy=True)

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)

    # Define relationship with ServiceRequest
    service_requests = db.relationship('ServiceRequest', back_populates='service', lazy=True)

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Reference to Customer
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)  # Reference to Professional
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='requested', nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    remarks = db.Column(db.Text, nullable=True)

    # Relationships to other models
    customer = db.relationship('Customer', back_populates='service_requests')
    service = db.relationship('Service', back_populates='service_requests')
    professional = db.relationship('Professional', back_populates='service_requests')
    review = db.relationship('Review', back_populates='service_request', lazy=True)

class Review(db.Model):
    __tablename__ = 'review'  # Ensure this has a table name
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    service_request = db.relationship('ServiceRequest', back_populates='review')  # Use back_populates for consistency
