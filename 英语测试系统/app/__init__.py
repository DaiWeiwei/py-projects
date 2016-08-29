from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

#from flaskext.mysql import MySQL
#mysql = MySQL()
app = Flask(__name__)
app.config.from_object('config')
#mysql.init_app(app)
db = SQLAlchemy(app)

from app import views, models
