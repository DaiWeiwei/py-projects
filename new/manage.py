from flask_script import Manager
from app import app, db
import sqlite3
from model import User

manager = Manager(app)


@manager.command
def ho():
	print("......")

@manager.option('-m', '--m', dest='msg_val', default='world')
def he(msg_val):
	print("000" + msg_val)

@manager.command
def init_db():
	# sql = 'create table user (id INT, name VARCHAR(10))'
	conn = sqlite3.connect('test.db')
	cursor = conn.cursor()
	sql = 'select * from user'
	# sql = "insert into user (id, name) VALUES (1, 'tony')"
	rets = cursor.execute(sql)
	# ret = cursor.fetchall()
	for ret in rets:
		print(ret)
	# conn.commit()
	cursor.close()
	conn.close()

@manager.command
def save():
	user = User(4, 'bony')
	# user.save()
	db.session.add(user)
	db.session.commit()


@manager.command
def query_all():
	users = User.query_all()
	for user in users:
		print(user)





if __name__ == '__main__':
	manager.run()