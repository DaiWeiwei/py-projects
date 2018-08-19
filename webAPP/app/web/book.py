from flask import jsonify, Blueprint

from controller import Book
from helper import is_isbn_or_key

web = Blueprint('web', __name__)
@web.route('/book/search/<q>/<page>')
def search(q, page):
	isbn_or_key = is_isbn_or_key(q)
	if isbn_or_key == 'isbn':
		result = Book.search_by_isbn(q)
	else:
		result = Book.search_by_keyword(q)
	return jsonify(result)
	# return json.dumps(result),200,{'constent-type':'application/json'}