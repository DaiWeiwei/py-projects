from flask import Flask, jsonify

from controller import Book
from helper import *

app = Flask(__name__)
app.config.from_object('config')





if __name__ == '__main__':
	app.run()


