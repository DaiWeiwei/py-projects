from flask import Flask
from flask import render_template
import os, sys, string
import MySQLdb
app=Flask(__name__)  
@app.route('/')  
def hello_world():  
    return app.send_static_file('index.html')
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
if __name__ == '__main__':  
    app.run(debug=True)  
