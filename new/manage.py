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

@manager.command
def init_db():
	# sql = 'create table user (id INT, name VARCHAR(10))'
	conn = sqlite3.connect('test.db')
	cursor = conn.cursor()
	sql = 'select * from user'
	# sql = "insert into user (id, name) VALUES (1, 'tony')"
	cursor.execute(sql)
	ret = cursor.fetchall()
	print(ret)
	# conn.commit()
	cursor.close()
	conn.close()




if __name__ == '__main__':
	manager.run()