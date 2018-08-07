from flask import Flask
from helper import *

app = Flask(__name__)
app.config.from_object('config')


app.route('/book/search/<q>/<page>')
def search(q, page):
	isbn_or_key = is_isbn_or_key(q)
