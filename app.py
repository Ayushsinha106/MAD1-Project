from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

import config

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"

import models

# import routes

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
