import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#base_dir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config.from_object("config")
app.config('SQLALCHEMY_DATABASE_URI') = 'mysql+pymysql://root:root@localhost:3306/f_db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 

db = SQLAlchemy(app)

from app import views, models