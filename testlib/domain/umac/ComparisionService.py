# coding:utf-8

import re
import time
import csv
import os
import sys
import glob
import difflib
import codecs
from difflib import Differ
from robot.api import logger
from pyh import *

##from testlib.domain.umac.umacconfig import UmacConfig




class ComparisionService(object):
#内存对比总入口
    @staticmethod
    def memeory_comparision(before_path,after_path,save_path):

##        umac_config = uMacService.find_umac_config(umac_name)
##        before_path=umac_config.cmd_memory_dir(0)
##        after_path=umac_config.cmd_memory_dir(1)
        if os.path.exists(before_path + '\\before.html'):
            os.remove(before_path + '\\before.html')
        if os.path.exists(after_path + '\\after.html'):
            os.remove(after_path + '\\after.html')
        before_memeory=ComparisionService.read_txt_file(before_path)
        length1 = len(before_memeory)
        after_memory=ComparisionService.read_txt_file(after_path)
        length2 = len(after_memory)
        page, tb = ComparisionService.html_template(before_path, after_path, before_memeory, after_memory)
        for i in before_memeory:
            for j in after_memory:
                if i.split(',')[0]==j.split(',')[0]:
                    if not i.split(',')[1]==j.split(',')[1] or not i.split(',')[2]==j.split(',')[2] or not i.split(',')[3]==j.split(',')[3]:
                        tb<<tr(td('changed item') + td(i) + td(j) + td(int(j.split(',')[3])-int(i.split(',')[3])), bgColor ='#6959CD')
                    # else:
                    #     tb<<tr(td('no change') + td(i) + td(j) + td(0))
                    break
        if length1 > length2:
            before_more = (item for item in before_memeory if item not in [value.split(',')[0] for value in after_memory])
            for item in before_more:
                tb<<tr(td('deleted item') + td(item) + td('None'), bgColor='#F08080')
        elif length1 < length2:
            after_more = (item for item in after_memory if item not in [value.split(',')[0] for value in before_memeory])
            for item in after_more:
                tb<<tr(td('new item')+ td('None') + td(item), bgColor='#00EE76')

        tb<<tr(td(' ') + td(a('before upgrade memory data',target='_blank', href=before_path+'\\before.html')) + td(a('after upgrade memory data',target='_blank', href=after_path+'\\after.html')))
        page.printOut(save_path, 'a')


        # d = difflib.HtmlDiff(wrapcolumn=80)
        # dd = d.make_file(before_memeory, after_memory, context=True).replace("charset=ISO-8859-1","charset=UTF-8",1)
        # with open(outpath, 'a') as f:
        #     f.write('\n***内存对比***\n' + dd)

        # last_data=ComparisionService.compare_memeory_data(before_memeory,after_memory)
        # file_name=outpath+'\\Memory_compare_result.csv'
        # ComparisionService.delete_file(file_name)

        # if len(last_data)>0 :
        #     ComparisionService.write_memory_data(last_data,outpath)


#创建页面模板
    @staticmethod
    def html_template(before_path, after_path, s1, s2):
        save_path1 = before_path + '\\before.html'
        save_path2 = after_path + '\\after.html'
        
        page = PyH('summary result')
        page<<h2('3.memory comparison:')
        div1 = page<<div(id='div1')
        table1 = div1<<table(border='2',id='memory')
        headtr = table1<<tr(id='headline', bgColor="#836FFF")<<th('compared result')<<th('before upgrade')<<th('after upgrade')<<th('''left memory comparison
                                                                                                                                        (after - before)''')


        page2 = PyH('result')
        page2<<h1('memory data', align='center')
        div2 = page2<<div(id='div2')
        table_before = div2<<table(border='2',id='memory')
        headtr = table_before<<tr(id='headline')<<th('board')<<th('total')<<th('used')<<th('free')
        for i in s1:
            table_before<<tr(td(i.split(',')[0]) + td(i.split(',')[1]) + td(i.split(',')[2]) + td(i.split(',')[3]))
        page2.printOut(save_path1)
        
        page3 = PyH('result')
        page3<<h1('memory data', align='center')
        div3 = page3<<div(id='div3')
        table_after = div3<<table(border='2',id='memory')
        headtr = table_after<<tr(id='headline')<<th('board')<<th('total')<<th('used')<<th('free')
        for i in s2:
            table_after<<tr(td(i.split(',')[0]) + td(i.split(',')[1]) + td(i.split(',')[2]) + td(i.split(',')[3]))
        page3.printOut(save_path2)

        return page, table1


#读取内存文本文件
    @staticmethod
    def read_txt_file(path):
        memeorylist=[]
        FileNames=os.listdir(path)
        # print FileNames
        if (len(FileNames)>0):
          for fn in FileNames:
            fullfilename=os.path.join(path,fn)
            # print fullfilename
            fileHandle=open(fullfilename)
            m=re.search('Mem:\s*(\d+)\s*(\d+)\s*(\d+)',fileHandle.read())
            try:
                memeorylist.append(fn.split('.')[0]+','+m.group(1)+','+m.group(2)+','+m.group(3))
            except Exception as e:
                logger.info(e)
                logger.info(u'可能由于网络原因没获取到%s内存') % fn
            fileHandle.close()
          return memeorylist

#对比内存数据
    @staticmethod
    def compare_memeory_data(before_data,after_data):
        last_data=[]
        before_num=len(before_data)
        after_num=len(after_data)
        if before_num<1 :
            return
        if after_num<1 :
            return
        for  i in range(0, before_num):
            for j in range (0,after_num):
               if before_data[i].split(',')[0]==after_data[j].split(',')[0]:
                  last_data.append(before_data[i]+','+after_data[j].split(',')[1]+','+after_data[j].split(',')[2]+','+after_data[j].split(',')[3])
        return last_data

#写入内存对比结果到文件
    @staticmethod
    def write_memory_data(memorydata,path):

        with open(path+'\\Memory_compare_result.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile,dialect='excel')
            spamwriter.writerow(['Board name', 'Total_Before', 'Used_Before', 'Free_Before', 'Total_After', 'Used_After', 'Free_After', 'Difference'])
            for i in range(0,len(memorydata)):
                difference=int(memorydata[i].split(',')[3])-int(memorydata[i].split(',')[6])
                spamwriter.writerow([memorydata[i].split(',')[0],memorydata[i].split(',')[1],memorydata[i].split(',')[2],memorydata[i].split(',')[3],memorydata[i].split(',')[4],memorydata[i].split(',')[5],memorydata[i].split(',')[6],str(difference)])
        csvfile.close()

#告警对比总入口
    @staticmethod
    def alarm_comparision(before_path,after_path,outpath):

        before_alarm=ComparisionService.read_csv_file(before_path)
        after_alarm=ComparisionService.read_csv_file(after_path)

        last_data=ComparisionService.campare_alarm_data(before_alarm,after_alarm)
        file_name=outpath+'\\Alarm_compare_result.csv'

        ComparisionService.delete_file(file_name)

##        outpath=umac_config.output_dir
        if len(last_data)>0 :
           ComparisionService.write_alarm_data(last_data,outpath)
        else:
            logger.info('There is no difference of Alarm')





#读取告警原始文件


    @staticmethod
    def read_csv_file(path):
        reload(sys)
        sys.setdefaultencoding('utf8');
        alarmlist=[]
        FileNames=os.listdir(path)

        if (len(FileNames)>0):
          for fn in FileNames:
            fullfilename=os.path.join(path,fn)
##            print fullfilename
            with open(fullfilename,'rb') as f:
              reader = csv.reader(f)
              for row in reader:
                 alarmlist.append(row[2].decode('utf-8','ignore')+';'+row[4].decode('utf-8','ignore'))
            f.close()
        return alarmlist

#告警文件内容对比
    @staticmethod
    def campare_alarm_data(before,after):
        alarm_result=[]
        after_alarm=after
        before_alarm=before



        # 取出升级后新增告警
        for i in after_alarm:
            if i not in before_alarm:
                alarm_result.append(i+';added')
       # 取出升级后删除的告警
        for j in before_alarm:
            if j not in after_alarm:
                alarm_result.append(j+';deleted')

        return alarm_result

#写入告警文件内容对比结果
    @staticmethod
    def write_alarm_data(alarmdata,path):
        reload(sys)
        sys.setdefaultencoding('utf8');
        with open(path+'\\Alarm_compare_result.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile,dialect='excel')
            spamwriter.writerow(['Location', 'Alarmcode', 'Deleted or Added'])
            for i in range(0,len(alarmdata)):
                spamwriter.writerow([alarmdata[i].split(';')[0].decode('utf-8','ignore').encode('gb2312'),alarmdata[i].split(';')[1].decode('utf-8','ignore').encode('gb2312'),alarmdata[i].split(';')[2].decode('utf-8','ignore').encode('gb2312')])
        csvfile.close()


#性能对比总入口
    @staticmethod
    def performance_comparision(before_path,after_path,outpath):
        before_performance=ComparisionService.performance_read_csv_file(before_path)
        logger.info(before_performance)
        logger.info('wwww')
        after_performance=ComparisionService.performance_read_csv_file(after_path)
        logger.info(after_performance)
        logger.info('rrrrrrr')

        last_data=ComparisionService.campare_performance_data(before_performance,after_performance)
        file_name=outpath+'\\performance_compare_result.csv'

        ComparisionService.delete_file(file_name)

##        outpath=umac_config.output_dir
        if len(last_data)>0 :
           ComparisionService.write_performance_data(last_data,outpath)
        else:
            logger.info('There is no difference of performance')


#读取性能任务原始文件


    @staticmethod
    def performance_read_csv_file(path):
        reload(sys)
        sys.setdefaultencoding('utf8');
        performancelist=[]
        FileNames=os.listdir(path)

        if (len(FileNames)>0):
          for fn in FileNames:
            fullfilename=os.path.join(path,fn)
##            print fullfilename
            with open(fullfilename,'rb') as f:
              reader = csv.reader( (line.replace('\00','') for line in f) )
              for row in reader:
                 performancelist.append(row[1].decode('utf-8','ignore')+';'+row[2].decode('utf-8','ignore'))
            f.close()
        return performancelist

#性能任务文件内容对比
    @staticmethod
    def campare_performance_data(before,after):
        performance_result=[]
        after_performance=after
        before_performance=before



        # 取出升级后新增任务
        for i in after_performance:
            if i not in before_performance:
                performance_result.append(i+';added')
       # 取出升级后删除任务
        for j in before_performance:
            if j not in after_performance:
                performance_result.append(j+';deleted')

        return performance_result

#写入性能任务文件内容对比结果
    @staticmethod
    def write_performance_data(performancedata,path):
        reload(sys)
        sys.setdefaultencoding('utf8');
        with open(path+'\\performance_compare_result.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile,dialect='excel')
            spamwriter.writerow(['performance', 'Deleted or Added'])
            for i in range(0,len(performancedata)):
                spamwriter.writerow([performancedata[i].split(';')[0].decode('utf-8','ignore').encode('gb2312'),performancedata[i].split(';')[1].decode('utf-8','ignore').encode('gb2312'),performancedata[i].split(';')[2].decode('utf-8','ignore').encode('gb2312')])
        csvfile.close()

#删除已经存在的文件
    @staticmethod
    def delete_file(filename):
##      print filename
      if os.path.exists(filename):
        os.remove(filename)

#信令跟踪对比总入口
    @staticmethod
    def compare_siginal(before_path,after_path,output_path,difference=True):
        before_file=ComparisionService.siginal_files_hb(before_path)
        after_file=ComparisionService.siginal_files_hb(after_path)
        ComparisionService.siginal_txt_html(before_file,after_file,output_path,difference)




#对比前合并所有信令跟踪文本文件到一个文件
    @staticmethod
    def siginal_files_hb(file_path):
        files = glob.glob(file_path+'\\*.txt')
        alltxtfile=file_path+'\\all_siginal.txt'
        if os.path.exists(alltxtfile):
           os.remove(alltxtfile)
        filewrite=open(alltxtfile,'w')
        for item in files:
            filetxt=codecs.open(item)
            lines=filetxt.read()
#如notepad，在保存一个以UTF-8编码的文件时，会在文件开始的地方插入三个不可见的字符（0xEF 0xBB 0xBF，即BOM）。
#因此我们在读取时需要自己去掉这些字符，Python中的codecs module定义了这个常量：
            if lines[:3] == codecs.BOM_UTF8:
               lines = lines[3:]
            filewrite.write('###############################################################################\n'+item+'\n###############################################################################\n')
            filewrite.write(lines)    #写入合并文件
            filetxt.close()
        filewrite.close()
        return alltxtfile

#进行对比以html文件格式展现
    @staticmethod
    def siginal_txt_html(before_file,after_file,output_path,difference=True):
        result_file=output_path+'\\all_comparison.html'
        if os.path.exists(result_file):
           os.remove(result_file)
        text1_lines = file(before_file).readlines()
        text2_lines = file(after_file).readlines()
        w=difflib.ndiff(text1_lines,text2_lines,)
##        print difference
        d = difflib.HtmlDiff(wrapcolumn=80)  #用HtmlDiff()类的make_file()方法就可以生成美观的HTML文档
        dd = d.make_file(text1_lines, text2_lines,context=difference).replace("charset=ISO-8859-1","charset=UTF-8",1)
        with open(result_file, 'a') as f:
             f.write('\n***信令跟踪对比***\n' + dd)
             f.close()

#进行对比以html文件格式展现
    @staticmethod
    def ipstack_txt_html(before_file,after_file,output_path,difference=True):
        result_file=output_path
        # if os.path.exists(result_file):
        #    os.remove(result_file)
        text1_lines = file(before_file).readlines()
        text2_lines = file(after_file).readlines()
        w=difflib.ndiff(text1_lines,text2_lines,)
##        print difference
        d = difflib.HtmlDiff(wrapcolumn=80)  #用HtmlDiff()类的make_file()方法就可以生成美观的HTML文档
        dd = d.make_file(text1_lines, text2_lines,context=difference).replace("charset=ISO-8859-1","charset=UTF-8",1)
        with open(result_file, 'a') as f:
             f.write('\n***协议栈对比***\n' + dd)
             f.close()



    @staticmethod
    def compare_ipstack(umac_config, save_path1, save_path2, save_path):
        s1 = file(save_path1).readlines()
        stack1 = [line for line in s1 if line!='\n' and line!='\r\n']
        s1=[]
        s2 = file(save_path2).readlines()
        stack2 = [line for line in s2 if line!='\n' and line!='\r\n']
        s2=[]
        page, tb = ComparisionService.html_ipstack()
        change = 0
        same_item = []
        if stack1 != stack2:
            diff = Differ()
            diff_list = diff.compare(stack1,stack2)
            for item in diff_list:
                if item.startswith('+'):
                    s2.append(item[1:])
                elif item.startswith('-'):
                    s1.append(item[1:])
            for item in s1:
                if item in s2:
                    same_item.append(item)
                    s2.remove(item)
            for item in same_item:
                s1.remove(item)
            for i in s1:
                change+=1
                tb<<tr(td('deleted item') + td(i) + td('None'), bgColor='#F08080')
            for i in s2:
                change+=1
                tb<<tr(td('new item')+ td('None') + td(i), bgColor='#00EE76')
        if not change:
            tb<<tr(td('no change') + td(a('before upgrade ipstack file',target='_blank', href=save_path1)) + td(a('after upgrade ipstack file',target='_blank', href=save_path2)))
        else:
            tb<<tr(td(' ') + td(a('before upgrade ipstack file',target='_blank', href=save_path1)) + td(a('after upgrade ipstack file',target='_blank', href=save_path2)))
        html_path_0 = '{0}/before_config_data.html'.format(umac_config.cmd_config_html_dir_0)
        html_path_1 = '{0}/after_config_data.html'.format(umac_config.cmd_config_html_dir_1)
        page<<h2('5.config data comparison:')
        tab = page<<table(border='2', id='html config')
        tab<<tr(td('before_file')+td('after_file'))
        tab<<tr(td(a('before upgrade config data', target='_blank', href=html_path_0)) + td(a('after upgrade config data', target='_blank', href=html_path_1)))
        page.printOut(save_path, 'a')

    @staticmethod
    def html_ipstack():
        page = PyH('summary result')
        page<<h2('4.ipstack comparison:')
        div1 = page<<div(id='div1')
        table1 = div1<<table(border='2',id='ipstack')
        headtr = table1<<tr(id='headline', bgColor="#836FFF")<<th('compared result')<<th('before upgrade')<<th('after upgrade')

        return page, table1
















































if __name__ == '__main__':
    ComparisionService.memeory_comparision('D:\\combo_mmegngp_sgsn_51\\before_upgrade\\memory',
                                                'D:\\combo_mmegngp_sgsn_51\\after_upgrade\\memory')
