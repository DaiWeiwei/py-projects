from app import app
from flask import render_template,request

@app.route('/')
def index():
    form = TodoForm()
    todos = Todo.objects.order_by('-time')
    return render_template("index.html",todos=todos, form=form)

@app.route('/add',methods=['POST',])
def add():
    content = request.form.get("content")
    todo = Todo(content=content)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'),404

if __name__ == '__main__':
    app.run()



