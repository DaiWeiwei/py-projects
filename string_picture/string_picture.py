from PIL import Image
import os

ascii_char = list(r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
pic = os.path.join(os.path.dirname(__file__), 'jobs.jpeg')
text = os.path.join(os.path.dirname(__file__), 'jobs.txt')

def get_char(r,g,b,alpha = 256):
	if alpha == 256:
		return ' '

	length = len(ascii_char)
	gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

	unit = (256+1)/length

	return ascii_char[int(gray / unit)]

if __name__ == '__main__':
	im = Image.open(pic)
	im = im.resize((80, 80), Image.NEAREST)

	txt = ''

	for i in range(80):
		for j in range(80):
			txt += get_char(*im.getpixel((j,i)))
			txt += '\n'

	print(txt)

	with open(text ,'w') as f:
		f.write(txt)
