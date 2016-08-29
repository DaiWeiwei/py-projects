#-*- coding: UTF-8 -*-
from flask import render_template, flash, redirect, jsonify, json
from flask import request,session
from app import app,models
from datetime import datetime
import sys
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/getUsers')
def getUsers():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    user=models.User.query.filter_by(username=username).all()
    return render_template('admin.html')
    results=[]
    for q in question:
        result={'id':q.id,'username':q.username,"type:":q.type}
        results.append(result)    
    json_result = {'result':results}
    return json.dumps(json_result,ensure_ascii=False)
