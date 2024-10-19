from models import db
from app import app
import uuid
import datetime

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database has been reset.")
print(datetime.datetime.utcnow())