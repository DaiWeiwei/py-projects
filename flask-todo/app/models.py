from app import db
import datetime


class Todo(db.Model):
	__tablename__ = 'todo'
	content = db.Column(db.String(30), nullable=False)
	time = db.Column(db.TIMESTAMP, default=datetime.datetime.now())
	status = db.Column(db.Integer, default=0)
	def __repr__(self):
		return '<Todo %r>' % self.content
