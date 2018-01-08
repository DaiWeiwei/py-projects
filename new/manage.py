from flask_script import Manager
from app import app
import sqlite3


manager = Manager(app)


@manager.command
def ho():
	print("......")



if __name__ == '__main__':
	manager.run()