from flask import jsonify,request

from . import web
from controller import Book
from helper import is_isbn_or_key


@web.route('/book/search')
def search():
	q = request.args.get('q')
	isbn_or_key = is_isbn_or_key(q)
	if isbn_or_key == 'isbn':
		result = Book.search_by_isbn(q)
	else:
		result = Book.search_by_keyword(q)
	return jsonify(result)
	# return json.dumps(result),200,{'constent-type':'application/json'}