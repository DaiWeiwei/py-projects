#-*- coding: UTF-8 -*-
from flask import render_template, flash, redirect, jsonify, json
from flask import request, session
from flask.ext.login import logout_user
from app import app,models
from .forms import LoginForm
from app import models,db
from datetime import datetime
from sqlalchemy import func
import sys
import os, shutil, xlrd, simplejson

# index view function suppressed for brevity

def login_validate(html_name):
    if 'username' in session:
        return render_template(html_name)
    return redirect('/home')

@app.route('/')
def loginPage():
    # if 'username' in session:
    #     result = models.User.query.filter_by(username=session['username']).first()
    #     type = result.getType()
    #     if (type == 1):
    #         if str(result.level) == 'None':
    #             return redirect('test')
    #         else:
    #             return redirect('myGrade')
    #     elif (type == 2):
    #         return redirect('teacher')
    #     elif (type == 0):
    #         return redirect('admin')
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('Home.html')

@app.route('/phrase')
def phraseQuize():
    return login_validate('phrase.html')

@app.route('/confuse')
def confuseQuize():
    return login_validate('confuse.html')

@app.route('/fileinput')
def fileInput():
    return login_validate('fileinput.html')

@app.route('/myGrade')
def myGrade():
    return login_validate('myGrade.html')

@app.route('/grade')
def grade():
    return login_validate('grade.html')

@app.route('/problem')
def problem():
    return login_validate('problem.html')

@app.route('/test')
def test():
    return login_validate('test.html')

@app.route('/dictionary')
def dictionary():
    return login_validate('dictionary.html')



@app.route('/toLogin', methods = ['GET', 'POST'])
def toLogin():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    username = request.form['username']
    result = models.User.query.filter_by(username=username, password=request.form['password']).first()
    if result is None:     
        return render_template('Home.html', error='用户名密码错误')
    session['username'] = username
    session['id'] = result.getId()
    type = result.getType()
    if(type==1):
        if str(result.level)=='None':
            return redirect('test')
        else:
            return redirect('myGrade')
    elif(type==2):
        return redirect('teacher')
    elif(type==0):
        return redirect('admin')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('id', None)
    return redirect('/home')

@app.route('/searchUser')
def hello_world():
    json_result = None
    if 'username' in session:
        userType = None
        username = session['username']
        result = models.User.query.filter_by(username=username).first()
        if result is None:
            return json.dumps({'status': 'error'}, ensure_ascii=False)
        type = result.getType()
        if (type == 1):
            if str(result.level) == 'None':
                userType = 'test'
            else:
                userType = 'myGrade'
        elif (type == 2):
            userType = 'teacher'
        elif (type == 0):
            userType = 'admin'
        json_result = {'status': 'success', 'username': username, 'userType': userType}
        return json.dumps(json_result, ensure_ascii=False)
    json_result = {'status': 'error'}
    return json.dumps(json_result, ensure_ascii=False)


@app.route('/main')
def main():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    username=session['username']
    user=models.User.query.filter_by(username=username).first()
    level=user.level
    question=models.WordQuize.query.filter_by(level=level).order_by(func.random()).limit(50)
    results=[]
    result={}
    #result={'user_id': 2,'s':1}
    #{'id':+q.id,'question':+q.question,"option:":+q.option}
    for q in question:
        result={'id':q.id,'question':q.question,"option:":q.option}
    results.append(result)    
    json_result = {'result':results}#json.dumps(json_result)
    return login_validate('main.html')

@app.route('/getWordQuize')
def getWordQuize():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    username=session['username']
    user=models.User.query.filter_by(username=username).first()
    level=user.level
    question=models.WordQuize.query.filter_by(level=level).order_by(func.random()).limit(50)
    results=[]
    #result={'user_id': 2,'s':1}
    #{'id':+q.id,'question':+q.question,"option:":+q.option}
    for q in question:
        result={'id':q.id,'question':q.question,'option':q.option}
        results.append(result)
      
    json_result = {'result':results}#json.dumps(json_result)
    return json.dumps(json_result,ensure_ascii=False)


@app.route('/getConfuseQuize')
def getConfuseQuize():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    username = session['username']
    user = models.User.query.filter_by(username=username).first()
    level = user.level
    question = models.ConfuseQuize.query.filter_by(level=level).order_by(func.random()).limit(50)
    results = []
    #result={'user_id': 2,'s':1}
    #{'id':+q.id,'question':+q.question,"option:":+q.option}
    for q in question:
        result={'id':q.id,'question':q.question,'option':q.option}
        results.append(result)
    print results
    json_result = {'result':results}#json.dumps(json_result)
    return json.dumps(json_result,ensure_ascii=False)


@app.route('/getPhraseQuize', methods = ['GET', 'POST'])
def getPhraseQuize():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    key=request.form['key']
    val=request.form['val']
    if key=="0":
        level=val
        if level=="0":
            username=session['username']
            user=models.User.query.filter_by(username=username).first()
            level=user.level
        question=models.PhraseQuize.query.filter_by(level=level).limit(50)
    elif key=="1":
        question=models.PhraseQuize.query.filter_by(classify=val).limit(50)
    else:
        username=session['username']
        user=models.User.query.filter_by(username=username).first()
        level=user.level
        question=models.PhraseQuize.query.filter_by(level=level).limit(50)
    results=[]
    #result={'user_id': 2,'s':1}
    #{'id':+q.id,'question':+q.question,"option:":+q.option}
    for q in question:
        result={'id':q.id,'question':q.question,'option':q.option}
        results.append(result)
      
    json_result = {'result':results}#json.dumps(json_result)
    return json.dumps(json_result,ensure_ascii=False)


@app.route('/getTest')
def getTest():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    question=models.WordQuize.query.order_by(func.random()).limit(10)
    results=[]
    results2=[]
    results3=[]
    #result={'user_id': 2,'s':1}
    #{'id':+q.id,'question':+q.question,"option:":+q.option}
    for q in question:
        result={'id':q.id,'question':q.question,'option':q.option}
        results.append(result)
    question = models.ConfuseQuize.query.order_by(func.random()).limit(20)
    for q in question:
        result = {'id': q.id, 'question': q.question, 'option': q.option}
        results3.append(result)
    question=models.PhraseQuize.query.order_by(func.random()).limit(20)
    for q in question:
        result={'id':q.id,'question':q.question,'option':q.option}
        results2.append(result)
    json_result = {'result':results,'result2':results2, 'result3':results3}#json.dumps(json_result)
    print results
    print results2
    print results3
    return json.dumps(json_result,ensure_ascii=False)


@app.route('/add_word')  
def add_word():
    question="a"
    option="AB"
    answer="AAAAA"
    level=1
    user = models.WordQuize(
        question=question,
        option=option,
        answer=answer,
        level=level
    )
    db.session.add(user)
    db.session.commit()
    return "success"

@app.route('/saveWordQuize', methods = ['GET', 'POST'])  
def saveWordQuize():
    quizeId=request.form['id'].split(',')
    answer=request.form['answer'].split(',')
    count=0
    wrong=""
    wrong_answer=""
    for i in range(len(quizeId)):
        result=models.WordQuize.query.filter_by(id=quizeId[i]).first()
        if result.getAnswer()==answer[i]:
            count+=1
        else:
            wrong+=quizeId[i]+","
            wrong_answer+=answer[i]+","
    grade = models.Grade(
        username=session['username'],
        score=count,
        type="word_quize",
        quize_id = wrong[:-1],
        time=datetime.now(),
        wrong_answer=wrong_answer[:-1]
    )
    db.session.add(grade)
    db.session.commit()
    return "success"

@app.route('/saveConfuseQuize', methods = ['GET', 'POST'])
def saveConfuseQuize():
    print '1111111111111'
    quizeId=request.form['id'].split(',')
    answer=request.form['answer'].split(',')
    print quizeId
    print answer
    count=0
    wrong=""
    wrong_answer=""
    for i in range(len(quizeId)):
        result=models.ConfuseQuize.query.filter_by(id=quizeId[i]).first()
        if result.getAnswer()==answer[i]:
            count+=1
        else:
            wrong+=quizeId[i]+","
            wrong_answer+=answer[i]+","
    grade = models.Grade(
        username=session['username'],
        score=count,
        type="confuse_quize",
        quize_id=wrong[:-1],
        time=datetime.now(),
        wrong_answer=wrong_answer[:-1]
    )
    db.session.add(grade)
    db.session.commit()
    return "success"


@app.route('/savePhraseQuize', methods = ['GET', 'POST'])
def savePhraseQuize():
    quizeId=request.form['id'].split(',')
    answer=request.form['answer'].split(',')
    count=0
    wrong=""
    wrong_answer=""
    for i in range(len(quizeId)):
        result=models.PhraseQuize.query.filter_by(id=quizeId[i]).first()
        if result.getAnswer()==answer[i]:
            count+=1
        else:
            wrong+=quizeId[i]+","
            wrong_answer+=answer[i]+","
    grade = models.Grade(
        username=session['username'],
        score=count,
        type="phrase_quize",
        quize_id = wrong[:-1],
        time=datetime.now(),
        wrong_answer=wrong_answer[:-1]
    )
    db.session.add(grade)
    db.session.commit()
    return "success"


@app.route('/saveTest', methods=['GET', 'POST'])
def saveTest():
    quizeId=request.form['id'].split(',')
    answer=request.form['answer'].split(',')
    quizeId2=request.form['id2'].split(',')
    answer2=request.form['answer2'].split(',')
    quizeId3=request.form['id3'].split(',')
    answer3=request.form['answer3'].split(',')
    count=0
    wrong=""
    if len(quizeId)>0:

        for i in range(len(quizeId)):
            result=models.WordQuize.query.filter_by(id=quizeId[i]).first()
            if result.getAnswer()==answer[i]:
                count+=1
            else:
                wrong+=quizeId[i]+","
    if len(quizeId2)>0:
        for i in range(len(quizeId2)):
            result=models.PhraseQuize.query.filter_by(id=quizeId2[i]).first()
            if result.getAnswer()==answer2[i]:
                count+=1
            else:
                wrong+=quizeId2[i]+","
    if len(quizeId3) > 0:
        for i in range(len(quizeId3)):
            result = models.ConfuseQuize.query.filter_by(id=quizeId3[i]).first()
            if result.getAnswer() == answer3[i]:
                count += 1
            else:
                wrong += quizeId3[i] + ","
    
    user=models.User.query.filter_by(username=session['username']).first()
    if(count<15):
        result={'level':1}
    elif(count>=40):
        result={'level':3}
    else:
        result={'level':2}
    
    models.User.query.filter_by(username=session['username']).update(result)
    db.session.commit()
    return str(count)

    # return "success"

@app.route('/getGrade', methods = ['POST'])
def getGrade():
    username=session['username']
    grade=models.Grade.query.filter_by(username=username).order_by(models.Grade.id.desc()).first()
    result={}
    if not grade is None:
        result={'grade':grade.score,'quize':grade.quize_id,'id':grade.id}
    return json.dumps(result,ensure_ascii=False)
    
@app.route('/getWrongProblem', methods = ['GET', 'POST'])
def getWrongProblem():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    username=session['username']
    quizeId=request.form['quize'].split(',')
    results=[]
    
    if request.form['quize']!="":
        type=request.form['type']
        wrongAnswer=grade.wrong_answer.split(',')
        count=0;
        for q in quizeId:
            if type=="word":
                question=models.WordQuize.query.filter_by(id=q).first()
            elif type=="phrase":
                question=models.PhraseQuize.query.filter_by(id=q).first()
            result={'id':question.id,'question':question.question,'option':question.option,'answer':question.answer}
            results.append(result)
      
    json_result = {'result':results}#json.dumps(json_result)
    return json.dumps(json_result,ensure_ascii=False)

@app.route('/getProblem', methods = ['GET', 'POST'])
def getProblem():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    username=session['username']
    gradeId=request.form['id']
    results=[]
    grade=models.Grade.query.filter_by(id=gradeId).first()
    type=grade.getType()
    if grade.getQuizeId()!="":
        quizeId=grade.getQuizeId().split(',')
        wrongAnswer=grade.wrong_answer.split(',')
        count=0;
        for q in quizeId:
            if type=="word_quize":
                question=models.WordQuize.query.filter_by(id=q).first()
            elif type=="phrase_quize":
                question=models.PhraseQuize.query.filter_by(id=q).first()
            elif type=="confuse_quize":
                question = models.ConfuseQuize.query.filter_by(id=q).first()
            result={'id':question.id,'question':question.question,'option':question.option,'answer':question.answer,'wrongAnswer':wrongAnswer[count]}
            count=count+1
            results.append(result)
      
    json_result = {'result':results}#json.dumps(json_result)
    return json.dumps(json_result,ensure_ascii=False)

@app.route('/getMyGrade')
def getMyGrade():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    username=session['username']
    results=[]
    grade=models.Grade.query.filter_by(username=username).order_by(models.Grade.id.desc()).all()
    for q in grade:
        result={'id':q.id,'grade':q.score,'type':q.type,"time":q.time}
        results.append(result)
    
    json_result = {'result':results}
    return json.dumps(json_result,ensure_ascii=False)
    #return render_template('myGrade.html',result=result,results=json_result)
@app.route('/add_phrase')  
def add_phrase():
    question="a"
    option="AB"
    answer="AAAAA"
    level=1
    phrasedQuize = models.PhrasedQuize(
        question=question,
        option=option,
        answer=answer,
        level=level,
        type=type,
        kind=kind,
        classify=classify
    )
    db.session.add(phrasedQuize)
    db.session.commit()
    return "success"

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/toRegister', methods = ['GET','POST'])
def toRegister():
    username=request.form['username']
    password=request.form['password']
    type=request.form['type']
    user = models.User(
        username=username,
        password=password,
        type=type
    )
    db.session.add(user)
    db.session.commit()
    return render_template('Home.html')

@app.route('/searchWord', methods = ['GET', 'POST'])
def searchWord():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    word=request.form['word']
    result={'success':'false'}
    text=models.Dictionary.query.filter_by(word=word).first()
    if text!=None:
        result={'success':'true','chinese':text.chinese}
    return json.dumps(result,ensure_ascii=False)

@app.route('/teacher')
def teacher():
    return login_validate('teacher.html')

@app.route('/subject')
def subject():
    return login_validate('subject.html')

@app.route('/modify')
def modify():
    return login_validate('modify.html')

@app.route('/getMyStu')
def getMyStu():
    teacherId=session['id']
    user=models.User.query.filter_by(teacherId=teacherId).all()
    result={}
    results=[]
    #for q in user:
    #    grade=models.Grade.query.filter_by(username=q.username).all()
    #    for m in grade:
    #        result={'username':q.username,'grade':m.score,'time':m.time,'type':m.type}
    #        results.append(result)
    grade=models.Grade.query.all()
    for m in grade:
        result={'username':m.username,'grade':m.score,'time':m.time,'type':m.type}
        results.append(result)
    json_result = {'result':results}
    return json.dumps(json_result,ensure_ascii=False)

@app.route('/getSubject', methods = ['GET','POST'])
def getSubject():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    type=request.form['type']
    result={}
    results=[]
    question=[]
    if type=="word":
        question=models.WordQuize.query.all()
        for q in question:

            result={'id':q.id,'level':q.level,'question':q.question,'answer':q.answer,'option':q.option}
            results.append(result)
    elif type=="phrase":
        question=models.PhraseQuize.query.all()
        for q in question:
            result={'id':q.id,'level':q.level,'question':q.question,'answer':q.answer,'option':q.option,'type':q.type,'kind':q.kind,'classify':q.classify}
            
            results.append(result)
    elif type == "confuse":
            question = models.ConfuseQuize.query.all()
            for q in question:
                result={'id':q.id,'level':q.level,'question':q.question,'answer':q.answer,'option':q.option}

                results.append(result)
    json_result = {'result':results}
    return json.dumps(json_result,ensure_ascii=False)

@app.route('/delSubject', methods = ['GET','POST'])
def delSubject():
    subjectId=request.form['id']
    type=request.form['type']
    question={}
    if type=="word":
        question=models.WordQuize.query.filter_by(id=subjectId).first()
    elif type=="phrase":
        question=models.PhraseQuize.query.filter_by(id=subjectId).first()
    elif type=="confuse":
        question = models.ConfuseQuize.query.filter_by(id=subjectId).first()
    db.session.delete(question)
    db.session.commit()
    return "success"

@app.route('/getModify', methods = ['GET','POST'])
def getModify():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    subjectId=request.form['id']
    type=request.form['type']
    result={}
    if type=="word":
        q=models.WordQuize.query.filter_by(id=subjectId).first()
        result={'id':q.id,'level':q.level,'question':q.question,'answer':q.answer,'option':q.option}
    elif type=="confuse":
            q=models.ConfuseQuize.query.filter_by(id=subjectId).first()
            result={'id':q.id,'level':q.level,'question':q.question,'answer':q.answer,'option':q.option}
    elif type=="phrase":
        q=models.PhraseQuize.query.filter_by(id=subjectId).first()
        result={'id':q.id,'level':q.level,'question':q.question,'answer':q.answer,'option':q.option,'type':q.type,'kind':q.kind,'classify':q.classify}
    return json.dumps(result,ensure_ascii=False)

@app.route('/modifyQuize', methods = ['GET','POST'])
def modifyQuize():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    type = request.form['type']
    id=request.form['id']
    question = request.form['question']
    option = request.form['option']
    level = request.form['level']
    answer = request.form['answer']
    if id!='':
        if type=="word":
            result={'level':level,'question':question,'answer':answer,'option':option}
            models.WordQuize.query.filter_by(id=id).update(result)
        if type=="confuse":
            result={'level':level,'question':question,'answer':answer,'option':option}
            models.ConfuseQuize.query.filter_by(id=id).update(result)
        elif type=="phrase":
            kind=request.form['kind']
            classify=request.form['classify']
            result={'level':level,'question':question,'answer':answer,'option':option,'kind':kind,'classify':classify}
            models.PhraseQuize.query.filter_by(id=id).update(result)
    else:
        if type == 'word':
            quize = models.WordQuize(
                question=question,
                option=option,
                answer=answer,
                level=level
            )
            db.session.add(quize)
        elif type == 'confuse':
            quize = models.ConfuseQuize(
                question=question,
                option=option,
                answer=answer,
                level=level
            )
            db.session.add(quize)
        elif type == 'phrase':
            quize = models.PhraseQuize(
                question=question,
                option=option,
                answer=answer,
                level=level,
                type=0,
                kind=request.form['kind'],
                classify=request.form['classify']
            )
            db.session.add(quize)

    db.session.commit()
    return render_template('subject.html')

@app.route('/newQuize', methods = ['GET','POST'])
def newQuize():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    type=request.form['type']
    question=request.form['question']
    option=request.form['option']
    level=request.form['level']
    answer=request.form['answer']
    
    db.session.commit()
    return question


@app.route('/admin')
def admin():
    return login_validate('admin.html')

@app.route('/modifyUser')
def modifyUser():
    return render_template('modifyUser.html')

@app.route('/getUsers')
def getUsers():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    user=models.User.query.all()
    results=[]
    for q in user:
        result={'id':q.id,'username':q.username,"type":q.type}
        results.append(result)    
    json_result = {'result':results}
    return json.dumps(json_result,ensure_ascii=False)
@app.route('/getModifyUser', methods = ['GET','POST'])
def getModifyUser():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    id=request.form['id']
    q=models.User.query.filter_by(id=id).first()
    result={'id':q.id,'username':q.username,'password':q.password, 'type': q.type}
    return json.dumps(result,ensure_ascii=False)

@app.route('/modifyUserForm', methods = ['GET','POST'])    
def modifyUserForm():
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    id=request.form['userId']
    # username=request.form['username']
    password=request.form['password']
    type=request.form['type']
    result={'type':type,'password':password}
    models.User.query.filter_by(id=id).update(result)
    db.session.commit()
    return 'success'
@app.route('/delUser', methods = ['GET','POST'])    
def delUser():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    id=request.form['id']
    user=models.User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return 'success'


def rmdirs(routerPath):
    filelist = os.listdir(routerPath)
    for f in filelist:
        filepath = os.path.join(routerPath, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)

def wordFile(filePath):
    print 'word'
    data = xlrd.open_workbook(filePath)
    from_sheet = data.sheet_by_index(0)
    ncols_length = from_sheet.ncols
    # 获取列数
    nrows_length = from_sheet.nrows
    # 获取行数

    dataSet = [[] for i in range(0, (nrows_length - 1))]
    for var1 in range(1, nrows_length):
        temp = from_sheet.row_values(var1)
        quize = models.WordQuize(
            answer=temp[0],
            level=temp[1],
            question=temp[2],
            option=temp[3]
        )
        db.session.add(quize)
    db.session.commit()


def phraseFile(filePath):
    data = xlrd.open_workbook(filePath)
    from_sheet = data.sheet_by_index(0)
    ncols_length = from_sheet.ncols
    # 获取列数
    nrows_length = from_sheet.nrows
    # 获取行数

    dataSet = [[] for i in range(0, (nrows_length - 1))]
    for var1 in range(1, nrows_length):
        temp = from_sheet.row_values(var1)
        quize = models.PhraseQuize(
            answer=temp[0],
            level=temp[1],
            question=temp[2],
            option=temp[3],
            type=temp[4],
            kind=temp[5],
            classify=temp[6]
        )
        db.session.add(quize)
    db.session.commit()

def dictFile(filePath):
    data = xlrd.open_workbook(filePath)
    from_sheet = data.sheet_by_index(0)
    ncols_length = from_sheet.ncols
    # 获取列数
    nrows_length = from_sheet.nrows
    # 获取行数

    dataSet = [[] for i in range(0, (nrows_length - 1))]
    for var1 in range(1, nrows_length):
        temp = from_sheet.row_values(var1)
        quize = models.Dictionary(
            word=temp[0],
            chinese=temp[1]
        )
        db.session.add(quize)
    db.session.commit()

def confuseFile(filePath):
    data = xlrd.open_workbook(filePath)
    from_sheet = data.sheet_by_index(0)
    ncols_length = from_sheet.ncols
    # 获取列数
    nrows_length = from_sheet.nrows
    # 获取行数

    dataSet = [[] for i in range(0, (nrows_length - 1))]
    for var1 in range(1, nrows_length):
        temp = from_sheet.row_values(var1)
        quize = models.ConfuseQuize(
            answer=temp[0],
            level=temp[1],
            question=temp[2],
            option=temp[3]
        )
        db.session.add(quize)
    db.session.commit()

@app.route('/file/', methods=['POST'])
def k_view():
    baseDir = os.path.dirname(__file__) + '/tmp/'
    rmdirs(baseDir)
    file = request.files['file']
    filetype = request.form['filetype']
    print filetype
    filePath = baseDir + file.filename
    try:
        file.save(filePath)
    except Exception as e:
        print e
        return simplejson.dumps({'error': 'upload failed'})

    filetypes = {
        'word': lambda: wordFile(filePath),
        'dict': lambda: dictFile(filePath),
        'phrase': lambda: phraseFile(filePath),
        'confuse': lambda: confuseFile(filePath)
    }
    try:
        filetypes[filetype]()
        return simplejson.dumps({'success': 'succeed'})
    except Exception as e:
        print e
        return simplejson.dumps({'error': 'failed'})
    finally:
        rmdirs(baseDir)
