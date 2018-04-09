# -*- coding: utf-8 -*-
import random


from flask import Flask, render_template, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
# from flask_sqlalchemy import SQLAlchemy
# from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'its hard to guess'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/f_db'
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# bootstrap = Bootstrap(app)

# db = SQLAlchemy(app)

class GuessNumberForm(FlaskForm):
 	number = IntegerField("text", validators=[
 		DataRequired("Input a valid integer!"),
 		NumberRange(0, 1000, 'Number range is 0~1000!')])
 	submit = SubmitField("submit")

@app.route("/")
def index():
	# 生成一个0~1000的随机数，存储到session变量里。
	session["number"] = random.randint(0,1000)
	session['times'] = 10
	return render_template('index.html')

@app.route("/guess", methods=["GET", "POST"])
def guess():
	times = session.get("times")
	result = session.get("number")
	form = GuessNumberForm()
	if form.validate_on_submit():
		times -= 1
		session['times'] = times
		if times == 0:
			flash("you lose")
			return redirect(url_for("index"))
		answer = form.number.data
		# flash("****************")
		print(answer,result,times)
		if answer>result:
			flash(f"{answer} is too large,left {times} times")
		elif answer<result:
			flash(f"{answer} is too small,left {times} times")
		else:
			flash("you win")
			return redirect(url_for("index"))
		return redirect(url_for('guess'))
	return render_template('guess.html', form=form)

# @app.route("/guess", methods=["GET"])
# def _guess():
# 	return render_template('guess.html', form=None)

 

if __name__ == '__main__':
	app.run(debug=True)


