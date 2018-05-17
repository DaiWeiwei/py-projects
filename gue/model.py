# import sqlite3
import pymysql
from app import db

# def get_conn():
# 	# return sqlite3.connect("test.db")
# 	host = '127.0.0.1'
# 	port = 3306
# 	db = 'f_db'
# 	user = 'root'
# 	pwd = 'root'
# 	conn = pymysql.connect(host=host,
# 	                       user=user,
# 	                       password=pwd,
# 	                       db=db,
# 	                       port=port,
# 	                       charset='utf8')
# 	return conn
#
# class User:
# 	def __init__(self, user_id, user_name):
# 		self.user_id = user_id
# 		self.user_name = user_name
#
# 	def save(self):
# 		sql = "insert into user VALUES (%s, %r)"   ####
# 		conn = get_conn()
# 		cursor = conn.cursor()
# 		cursor.execute(sql, (self.user_id, self.user_name))
# 		conn.commit()
# 		cursor.close()
# 		conn.close()
#
# 	@staticmethod
# 	def query():
# 		sql = 'select * from user'
# 		conn = get_conn()
# 		cursor = conn.cursor()
# 		cursor.execute(sql)
# 		rows = cursor.fetchall()
# 		users = []
# 		for row in rows:
# 			user = User(row[0], row[1])
# 			users.append(user)
# 		cursor.close()
# 		conn.close()
#
# 		return users
#
# 	def __str__(self):
# 		return 'id:{}--name:{}'.format(self.user_id, self.user_name)

class User(db.Model):
	# __tablename__ = 'user'
	user_id = db.Column(db.Integer, primary_key=True)
	user_name = db.Column(db.String)

	def __init__(self, user_id, user_name):
		self.user_id = user_id
		self.user_name = user_name

	def __str__(self):
		return '`user`:   id:{}--name:{}'.format(self.user_id, self.user_name)

