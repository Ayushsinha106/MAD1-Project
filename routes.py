from flask import Flask, request, render_template

from models import db, User, Service, ServiceRequest, Review

from app import app

@app.route('/')
def index():
    return render_template('index.html')