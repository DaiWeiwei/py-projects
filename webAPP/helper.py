def is_isbn_or_key(word):
	'''
	判断url参数是关键字还是isbn
	:param word:
	:return:
	'''
	isbn_or_key = 'key'
	if len(word) == 13 and word.isdigit():
		isbn_or_key = 'isbn'
	short_word = word.repalce('-', '')
	if '-' in word and len(short_word) == 10 and short_word.isdigit():
		isbn_or_key = 'isbn'
	return isbn_or_key
