#coding=utf-8
import win32clipboard as w
import win32con
import os
import re
import inspect
import sys


def getText():
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    return d

def setText(aString):
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_TEXT, aString)
    w.CloseClipboard()

def savefile():
    this_file=inspect.getfile(inspect.currentframe())
    path=os.path.abspath(os.path.dirname(this_file))
    fff=getText()
    f=open(path+'\www.txt','w')
    f.write(fff)
    f.close()

def save_inddcfg():#保存独立单板的配置
    savefile()
    this_file=inspect.getfile(inspect.currentframe())
    path=os.path.abspath(os.path.dirname(this_file))
    n=open(path+'\www.txt','r')
    txtlist=[]
    indlist=[]
    indidlist=[]
    ind_detail=[]

    lines=n.readlines()

    for line in lines:
        if line.find('CMM')!= -1:
            ind_detail.append('ECMM')
            p = re.compile('\d{1,3}')

            indlist=p.findall(line)
            indidlist=indidlist+indlist[0:1]
            ind_detail=ind_detail+indlist[0:3]
        if line.find('BASE')!= -1:
            ind_detail.append('EGBS')
            p = re.compile('\d{1,3}')
            indlist=p.findall(line)
            indidlist=indidlist+indlist[0:1]
            ind_detail=ind_detail+indlist[0:3]
        if line.find('Base')!= -1:
            ind_detail.append('EGBS')
            p = re.compile('\d{1,3}')
            indlist=p.findall(line)
            indidlist=indidlist+indlist[0:1]
            ind_detail=ind_detail+indlist[0:3]

        if line.find('FABRIC')!= -1:
            ind_detail.append('EGFS')
            p = re.compile('\d{1,3}')
            indlist=p.findall(line)
            indidlist=indidlist+indlist[0:1]
            ind_detail=ind_detail+indlist[0:3]

        if line.find('Fabric')!= -1:
            ind_detail.append('EGFS')
            p = re.compile('\d{1,3}')
            indlist=p.findall(line)
            indidlist=indidlist+indlist[0:1]
            ind_detail=ind_detail+indlist[0:3]
        p = re.compile('\d+\.\d+\.\d+\.\d+')
        indlist=p.findall(line)
        if indlist:
         txtlist=txtlist+indlist

    n.close()

    n=open(path+'\indd.txt','w')
    for i in txtlist:
     n.writelines(i+'\n')
    n.close()

    n=open(path+'\inddid.txt','w')
    for i in indidlist:
     n.writelines(i+'\n')
    n.close()
    n=open(path+'\inddetail.txt','w')
    for i in ind_detail:
     n.writelines(i+'\n')
    n.close()

def save_addindver():#保存独立单板添加版本信息
    addindver=[]
    savefile() #剪贴板的内容报保存到文件
    this_file=inspect.getfile(inspect.currentframe())
    path=os.path.abspath(os.path.dirname(this_file))
    n=open(path+'\www.txt','r') #读取该文件
    lines=n.readlines()
    for line in lines:
        r=re.compile('\EGBS\_\w+\.\w+\.\d+\.\d+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\EGBS\_\w+\.\w+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\EGFS\_\w+\.\w+\.\d+\.\d+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\EGFS\_\w+\.\w+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\ECMM\_\w+\.\w+\.\d+\.\d+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
    n.close()


    n=open(path+'\indaddver.txt','w')
    print addindver
    for i in addindver:
     n.writelines(i+'\n')
    n.close()

def save_indrunver():#保存独立单板运行版本信息
    addindver=[]
    savefile() #剪贴板的内容报保存到文件
    this_file=inspect.getfile(inspect.currentframe())
    path=os.path.abspath(os.path.dirname(this_file))
    n=open(path+'\www.txt','r') #读取该文件
    lines=n.readlines()
    for line in lines:
        r=re.compile('\EGBS\_\w+\.\w+\.\d+\.\d+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\EGBS\_\w+\.\w+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\EGFS\_\w+\.\w+\.\d+\.\d+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\EGFS\_\w+\.\w+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
        r=re.compile('\ECMM\_\w+\.\w+\.\d+\.\d+\.\d+\_\d+\.pkg')
        if len(r.findall(line))!=0: #如果发现则写入列表
              addindver=addindver+r.findall(line)
              r=re.compile('\s{1}\d{9}')
              if len(r.findall(line))!=0: #如果发现则写入列表
                      addindver=addindver+r.findall(line)
    n.close()

    n=open(path+'\indrunver.txt','w')
    for i in addindver:
     n.writelines(i+'\n')
    n.close()

def save_showcmd():#保存查询命令
    showcmd=[]
    savefile() #剪贴板的内容报保存到文件
    this_file=inspect.getfile(inspect.currentframe())
    path=os.path.abspath(os.path.dirname(this_file))
    type = sys.getfilesystemencoding()
    n=open(path+'\www.txt','r') #读取该文件
    lines=n.readlines()
    for line in lines:

        ss='Show Level'
        tt='数据查看级别'
        tt=tt.decode('UTF-8').encode(type)
##        print line

        pos=line.find(ss)
        if pos<0:  #英文找不到，按中文找
           pos=line.find(tt) #中文版本
        if pos>0: # 找到情况下，截取show命令放入列表
           showcmd.append(line[8:pos-1])

    n.close()
##    print tt
##    print showcmd

    n=open(path+'\showcmd.txt','w')  #批量show命令保存到文件
    for i in showcmd:
     n.writelines(i+'\n')
    n.close()







##    w=len(txtlist)
##    if w==11 :
##        h=3
##    if w==15:
##        h=6
##    if w==18:
##        h=9
##    multilist = [[0 for col in range(4)] for row in range(h)]
##    print(w)
##    for item in txtlist:
##        if item.find('CMM')!= -1:
##            p = re.compile('\d{1,3}')
##            print p.findall(item)
##            if h==3:
##              pass
##            ##p = re.compile('\')
##            print(item)
##
##    print multilist
##    print os.getcwd()
##    wwww=['ECMM','WWW','ECMM','ECMM']
##    print wwww.count('ECMM')





if __name__ == '__main__':
    save_showcmd()

##    n=open('d:\www.txt','r')
##    txtlist=[]
##    count=0
##    lines=n.readlines()
##    for line in lines:
##        txtlist.append(line)
##        count=count+1
##    n.close()
##    print txtlist[count-1]
##    pattern= re.compile(r'hello')
##    match= pattern.match('hello world!')
##    if match:

##     print match.group()

##    for item in txtlist:
##        print item[1]
##        print count




