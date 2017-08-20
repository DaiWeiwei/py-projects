from app import app
from flask import render_template



@app.route('/')
def index():
    # return render_template("index.html",text="GYY")
    return "GYY,I love you!!!!!"

if __name__ == '__main__':
    app.run()



