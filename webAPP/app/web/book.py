from flask import jsonify,request

from app.forms.book import SearchForm
from . import web
from controller import Book
from helper import is_isbn_or_key


@web.route('/book/search')
def search():
	# q = request.args.get('q')
	form = SearchForm(request.args)
	if form.validate():
		q = form.q.data.strip()
		page = form.page.data  #page默认值1
		isbn_or_key = is_isbn_or_key(q)
		if isbn_or_key == 'isbn':
			result = Book.search_by_isbn(q)
		else:
			result = Book.search_by_keyword(q, page)
		return jsonify(result)
		# return json.dumps(result),200,{'constent-type':'application/json'}
	else:
		return jsonify(form.errors)