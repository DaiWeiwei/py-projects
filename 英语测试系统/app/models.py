from app import db
from datetime import datetime
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(64))
    username= db.Column(db.String(64))
    password = db.Column(db.String(120))
    level=db.Column(db.SmallInteger)
    type=db.Column(db.Integer)
    teacherId=db.Column(db.Integer)
    #def login(username,password):
    def getType(self):
        return self.type
    def getId(self):
        return self.id
    def setLevel(self,level):
        self.lelve=level

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(64))
    username= db.Column(db.String(120))
    score = db.Column(db.Integer)
    type=db.Column(db.String(64))
    quize_id= db.Column(db.String(120))
    time=db.Column(db.DateTime)
    wrong_answer=db.Column(db.String(120))
    def __init__(self,username, score, type,quize_id,time,wrong_answer):
        self.username = username
        self.score = score
        self.type = type
        self.quize_id = quize_id
        self.time=time
        self.wrong_answer=wrong_answer
    def getQuizeId(self):
        return self.quize_id
    def getType(self):
        return self.type
class WordQuize(db.Model):
    __tablename__ = 'word_quize'
    id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(64))
    question= db.Column(db.String(64))
    option = db.Column(db.String(120))
    answer=db.Column(db.String(64))
    level=db.Column(db.SmallInteger)
    #def login(username,password):        
    #def __repr__(self):
    #    return '%s (%r, %r)' % (self.__class__.__name__, self.id, self.question)
    def __init__(self, question, option, answer,level):
        self.question = question
        self.option = option
        self.answer = answer
        self.level = level
    def getAnswer(self):
        return self.answer
class PhraseQuize(db.Model):
    __tablename__ = 'phrase_quize'
    id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(64))
    question= db.Column(db.String(64))
    option = db.Column(db.String(120))
    answer=db.Column(db.String(64))
    level=db.Column(db.SmallInteger)
    type=db.Column(db.SmallInteger)
    kind = db.Column(db.String(64))
    classify=db.Column(db.String(64))
    def getAnswer(self):
        return self.answer
    #def login(username,password):        
    #def __repr__(self):
    #    return '%s (%r, %r)' % (self.__class__.__name__, self.id, self.question)
    def __init__(self, question, option, answer,level, type, kind, classify):
        self.question = question
        self.option = option
        self.answer = answer
        self.level = level
        self.type = type
        self.kind = kind
        self.classify = classify
class Dictionary(db.Model):
    __tablename__ = 'dictionary'
    id = db.Column(db.Integer, primary_key=True)
    word= db.Column(db.String(64))
    chinese = db.Column(db.String(120))
    def __init__(self, word, chinese):
        self.word = word
        self.chinese = chinese



class ConfuseQuize(db.Model):
    __tablename__ = 'confuse_quize'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(64))
    level = db.Column(db.SmallInteger)
    question = db.Column(db.String(64))
    option = db.Column(db.String(120))
    def __init__(self, question, option, answer,level):
        self.question = question
        self.option = option
        self.answer = answer
        self.level = level
    def getAnswer(self):
        return self.answer
