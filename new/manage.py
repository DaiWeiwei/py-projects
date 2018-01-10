from flask_script import Manager
from app import app
import sqlite3


manager = Manager(app)


@manager.command
def ho():
	print("......")

@manager.option('-m', '--m', dest='msg_val', default='world')
def he(msg_val):
	print("000" + msg_val)



if __name__ == '__main__':
	manager.run()