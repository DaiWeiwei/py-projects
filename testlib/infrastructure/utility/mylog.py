#coding=utf-8
import sys
import codecs
from FileOperation import FileOperation
import datetime

class MyLog(object):
    @staticmethod
    def init(output_path):
        MyLog._output_path = output_path
        file_name = '{0}/{1}.log'.format(output_path,FileOperation.get_file_name_of_current_time())
        MyLog._f = codecs.open(file_name,'wb','utf-8')
    @staticmethod
    def close():
        try:
            if MyLog._f:
                MyLog._f.close()
        except:
            pass

    @staticmethod
    def debug(content,flag):
        MyLog._out_put('debug',content,flag)

    @staticmethod
    def info(content,flag):
        MyLog._out_put('info',content,flag)

    @staticmethod
    def error(content):
        MyLog._out_put('error',content,flag=1)

    @staticmethod
    def _out_put(level,content,flag):
        try:
            if MyLog._f:
                if flag:
                    MyLog._f.write(u'[{0}] [{1}]:{2}\n'.format(datetime.datetime.now(),level,content))
                else:
                    MyLog._f.write(u'{0}\n'.format(content))

        except Exception,e:
            print u'_out_put error:{0}'.format(e)

def get_log():
    return MyLog()

def create_log(output_path):
    MyLog.init(output_path)
    return MyLog()

def release_log():
    MyLog().close()

