from PIL import Image


ascii_char = list(r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

def get_char(r,g,b,alpha):
	if alpha == 256:
		return ' '

	length = len(ascii_char)
	gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

	unit = (256+1)/length

	return ascii_char[int(gray / unit)]
