#coding:utf-8
import os
import re
import sys
import xml.dom.minidom
from pyh import *
from multiprocessing import Process,Pool,Manager

reload(sys)
sys.setdefaultencoding('utf8')

class Test(object):

    def __init__(self,args):
        self.dir_path0 = args[0] + '\\before_upgrade\\sigtrace\\after_wash'
        self.dir_path1 = args[0] + '\\after_upgrade\\sigtrace\\after_wash'
        self.output_path = args[0] + '\\output\\compared_sigtrace'
        self.save_path = args[0] + '\\output\\sig_comparison.html'
        self.xml_path = args[1]
        self.just_compare_send = int(args[2])

    def main(self):
        print 'Start compare sigtrace.'
        FileNames = os.listdir(self.dir_path0)
        filenames = os.listdir(self.dir_path1)
        # Filenames=FileNames if len(FileNames)<=len(filenames) else filenames
        if not FileNames or not filenames:
            raise Exception('没有源文件！')
        Filenames = [file for file in FileNames if file in filenames]
        more_files_before = [file for file in FileNames if file not in filenames]
        more_files_after = [file for file in filenames if file not in FileNames]
        xml_dict = Test.xml_to_dict(self.xml_path)
        params_dict = {
                    'dir_path0':self.dir_path0,
                    'dir_path1':self.dir_path1,
                    'output_path':self.output_path,
                    'just_compare_send':self.just_compare_send
                    }

        page_dict = Manager().dict()
        #进程数量，可修改
        process_num = 8
        #进程池中并发进程数量，默认为cpu核数
        pool = Pool()
        process_list = []
        step = len(Filenames)/process_num
        for i in xrange(process_num):
            file_number_list = range(i*step, (i+1)*step) if i != process_num-1 else range(i*step, len(Filenames))
            # process_list.append(Process(target=compare,args=(xml_dict,Filenames,params_dict,file_number_list,page_dict,i)))
            pool.apply_async(compare, (xml_dict,Filenames,params_dict,file_number_list,page_dict,i))
        # for i in xrange(process_num):
        #     process_list[i].start()
        # for i in xrange(process_num):
        #     process_list[i].join()
        pool.close()
        pool.join()
        for i in xrange(process_num):
            try:
                page_dict[i].printOut(self.save_path, 'a')
            except:
                print 'Process{0} has an error'.format(i)
        if more_files_before:
            page_before = Test.only_in_before_or_after(more_files_before,params_dict,before_is_more=1)
            page_before.printOut(self.save_path, 'a')
        if more_files_after:
            page_after = Test.only_in_before_or_after(more_files_after,params_dict,before_is_more=0)
            page_after.printOut(self.save_path, 'a')      
        print 'Sigtrace comparasion has been finished.'

    @staticmethod
    def read_txt_file(xml_dict, file_path,just_compare_send):
        # xmlnames=os.listdir(xml_path)
        # createVar = locals()
        content = file(file_path).readlines()
        content.append('\n')
        compare_dict = {}
        dict1 = {}
        count = 0
        start = 0
        # result = []
        length = len(content)
        for i in xrange(length):
            if 'Echo' in content[i] or '---------' in content[i] or '1|--Detailed' in content[i]:
                continue
            elif content[i].startswith('0|--'):
                if just_compare_send:
                    if not u'发送' in content[i]: 
                        continue
                list_dict = {}
                start +=1
                dict1[count] = content[i]
                protocol = content[i].split(' ')[0][4:].upper()
                if protocol=='EMM':
                    protocol = 'MM'
                elif protocol=='ESM':
                    protocol = 'SM'
                message = content[i].split('<')[1].strip().upper()
                try:
                    message_dict = xml_dict[protocol]
                except:
                    print '没有{0}的xml文件'.format(protocol)
                try:
                    rule_list = message_dict[message]
                except:
                    print 'xml中没有{0}'.format(message)
                general_dict = xml_dict['general']
                rule_list.extend(general_dict['general'])
                # result.append(content[i])
            elif content[i] != '\n':
                if start:
                    current_level = content[i].strip()[0]
                    if current_level == '1':
                        list_dict['1'] = []              
                        list_dict['1'].append(content[i])
                        continue
                    elif rule_list:                
                        for item in rule_list:
                            m = re.findall(item, content[i])
                            if m:                                               #过滤规则中的项
                                content[i] = content[i].strip().split(':')[0]
                                break                                           #只取字段，忽略值               
                    pre_level = content[i-1].strip()[0]
                    if current_level == pre_level:
                        list_dict[current_level].append(content[i].strip())
                    elif current_level > pre_level: 
                        list_dict[current_level] = [] 
                        list_dict[current_level].append(content[i].strip())
                        list_dict[pre_level].append(list_dict[current_level])
                    else:  
                        list_dict[current_level].append(content[i].strip())            
            else:
                if start:
                    if list_dict['1']:
                        compare_dict[count] = list_dict['1']
                        count+=1
                        start = 0
        return dict1, compare_dict, content

    @staticmethod
    def create_page(file_path, id, case_name, page=None,tab=None, module=None, left=None, right=None,is_current_case_over=0):
        if module==None and left==None and right==None:    #从用例层面判断是否有差异
            if id == 1:                                   #若为第一条用例，则初始化页面
                page = PyH('result')
                case_number = '({0})'.format(id)
                fullname = case_number+case_name
                page << h2(b('signal trace comparison'), align='center')
                page<<div(b(fullname,style='font-size:18px'))
                page << div(b('no change', style='color:green;'))
                page<<div(a('premitive file', target='_blank', href=file_path))
                tab = None
            else:
                if not page: page = PyH('result')
                case_number = '({0})'.format(id)
                fullname = case_number+case_name
                # page = PyH('result')               #若不是第一条用例，迭代page
                page<<b(fullname,style='font-size:18px')+br()
                page << div(b('no change', style='color:green;'))
                page<<div(a('premitive file', target='_blank', href=file_path))
                tab = None
        elif id == 1:
    #有差异时，判断是否为第一条用例，若是第一条用例下的第一条差异则初始化页面
    #若只是第一条用例，则迭代page tab
            if not is_current_case_over:
                page = PyH('result')
                case_number = '({0})'.format(id)
                fullname = case_number+case_name
                page << h2('signal trace comparison', align='center')
                page<<div(b(fullname,style='font-size:18px'))
                page<<div(a('premitive file', target='_blank', href=file_path))
                tab = page<<table(border='2')
                tab<<tr(th('before') + th('after'))
                tab<<tr(td(span(module,style='color:black;font-size:14px;')+br()+b(left,style='color:red;font-size:15px;')) + td(span(module,style='color:black;font-size:14px;')+br()+b(right, style='color:red;font-size:15px;')))
            else:
                tab<<tr(td(span(module,style='color:black;font-size:14px;')+br()+b(left,style='color:red;font-size:15px;')) + td(span(module,style='color:black;font-size:14px;')+br()+b(right, style='color:red;font-size:15px;')))
        elif is_current_case_over:
            tab<<tr(td(span(module,style='color:black;font-size:14px;')+br()+b(left,style='color:red;font-size:15px;')) + td(span(module,style='color:black;font-size:14px;')+br()+b(right, style='color:red;font-size:15px;')))
        else:
            if not page and not tab: page = PyH('result')
            case_number = '({0})'.format(id)
            fullname = case_number+case_name
            page<<div(b(fullname,style='font-size:18px'))
            page<<div(a('premitive file', target='_blank', href=file_path))
            tab = page<<table(border='2')
            tab<<tr(th('before') + th('after'))
            tab<<tr(td(span(module,style='color:black;font-size:14px;')+br()+b(left,style='color:red;font-size:15px;')) + td(span(module,style='color:black;font-size:14px;')+br()+b(right, style='color:red;font-size:15px;')))
        return page, tab

    @staticmethod
    def premitive_file(content1,content2,path):
        # def color_message_head():
        #     if content1[i].startswith('0|--') and content2[i].startswith('0|--'):
        #         tab<<tr(td('-'*k1 + content1[i],style='color:green;font-size:14px;')+td('-'*k2 + content2[i],style='color:green;font-size:14px;'))
        #     elif content1[i].startswith('0|--'):
        #         tab<<tr(td('-'*k1 + content1[i],style='color:green;font-size:14px;')+td('-'*k2 + content2[i],style='font-size:14px;'))                   
        #     elif content1[i].startswith('0|--'):
        #         tab<<tr(td('-'*k1 + content1[i],style='font-size:14px;')+td('-'*k2 + content2[i],style='color:green;font-size:14px;'))
        #     else:
        #         tab<<tr(td('-'*k1 + content1[i],style='font-size:14px;')+td('-'*k2 + content2[i],style='font-size:14px;'))
        length1 = len(content1)
        length2 = len(content2)
        length = abs(length1-length2)
        page = PyH('file')
        page<<h2('sigtrace data', align='center')
        tab = page<<table(border = '2')
        tab<<tr(th(b('before'))+th(b('after')))
        if length1 > 1 and length2>1:
            if length1 >= length2:
                for i in xrange(length2):
                    k1=0; k2=0
                    while content1[i][k1] == ' ':
                        k1+=1
                    while content2[i][k2] == ' ':
                        k2+=1
                    tab<<tr(td('-'*k1 + content1[i],style='font-size:14px;')+td('-'*k2 + content2[i],style='font-size:14px;'))
                for i in xrange(length2,length+length2):
                    k1=0
                    while content1[i][k1] == ' ':
                        k1+=1
                    tab<<tr(td('-'*k1 + content1[i],style='font-size:14px;')+td(' '))
            else:
                for i in xrange(length1):
                    k1=0; k2=0
                    while content1[i][k1] == ' ':
                        k1+=1
                    while content2[i][k2] == ' ':
                        k2+=1
                    tab<<tr(td('-'*k1 + content1[i],style='font-size:14px;')+td('-'*k2 + content2[i],style='font-size:14px;'))
                for i in xrange(length1,length+length1):
                    k2=0
                    while content2[i][k2] == ' ':
                        k2+=1
                    tab<<tr(td(' ')+td('-'*k2 + content2[i],style='font-size:14px;'))

        elif length1 <= 1:
            for i in xrange(length2):
                k = 0
                while content2[i][k] == ' ':
                    k+=1
                tab<<tr(td(' ')+td(b('-'*k + content2[i],style='font-size:14px;')))
        else:
            for i in xrange(length1):
                k = 0
                while content1[i][k] == ' ':
                    k+=1
                tab<<tr(td(b('-'*k + content1[i],style='font-size:14px;'))+td(' '))

        page.printOut(path)

    # @staticmethod
    # def premitive_file(content1,content2,path,init_flag):
        # if init_flag:
        #     page = PyH('file')
        #     page<<h2('sigtrace data', align='center')
        #     tab = page<<table(border = '2')
        #     tab<<tr(th(b('before'))+th(b('after')))
        # elif content1 and content2:
        # elif not content1:
        #     for i in xrange(content2):
        #         k = 0
        #         while content2[i][k] == ' ':
        #             k+=1
        #         tab<<tr(td(' ')+td(b('-'*k + content2[i],style='color:red;font-size:14px;')))
        # else:
        #     for i in xrange(content1):
        #         k = 0
        #         while content1[i][k] == ' ':
        #             k+=1
        #         tab<<tr(td(b('-'*k + content1[i],style='color:red;font-size:14px;'))+td(' '))

    @staticmethod
    def xml_to_dict(xml_path):
        xml_dict = {}
        xmlnames=os.listdir(xml_path)
        for item in xmlnames:
            message_dict = {}
            xml_abspath = os.path.join(xml_path, item)
            protocol = item.split('.')[0]
            dom = xml.dom.minidom.parse(xml_abspath)
            filter_list = dom.documentElement.getElementsByTagName('Filter')
            general_list = dom.documentElement.getElementsByTagName('General')
            if filter_list:
                for tag in filter_list:
                    rule = tag.getAttribute('Input')
                    message = tag.getAttribute('Message')
                    if message_dict.has_key(message):
                        if rule not in message_dict[message]:
                            message_dict[message].append(rule.encode('utf-8'))
                    else:
                        message_dict[message] = [rule.encode('utf-8')]
            if general_list:
                for tag in general_list:
                    rule = tag.getAttribute('Input')
                    message = tag.getAttribute('Message')
                    if message_dict.has_key(message):
                        message_dict[message].append(rule.encode('utf-8'))
                    else:
                        message_dict[message] = [rule.encode('utf-8')]
            xml_dict[protocol] = message_dict
        return xml_dict
    
    @staticmethod
    def only_in_before_or_after(filename_list,path_dict,before_is_more):
        for index,filename in enumerate(filename_list):
            id = filename.split('@')[0]
            case_name = filename.split('.')[0].decode('gbk')
            file_path = '{1}\\{0}.html'.format(id,path_dict['output_path'])
            if before_is_more:
                fullfilename1 = os.path.join(path_dict['dir_path0'],filename)
                content1 = file(fullfilename1).readlines()
                Test.premitive_file(content1,'',file_path)                   
            else:
                fullfilename2 = os.path.join(path_dict['dir_path1'],filename)
                content2 = file(fullfilename2).readlines()
                Test.premitive_file('',content2,file_path)
            if not index:
                page,tab = Test.before_or_after_page(file_path,case_name,before_is_more,None,None)
            else:
                page,tab = Test.before_or_after_page(file_path,case_name,before_is_more,page,tab) 
        return page

    @staticmethod
    def before_or_after_page(file_path,case_name,before_is_more,page,tab):        
        if before_is_more:
            if not page:
                page = PyH('result')
                page<<br()<<br()
                page<<div(b('升级前存在，升级后不存在的信令',style='font-size:18px'))
                tab = page<<table(border='2')
                tab<<tr(th('before') + th('after'))
                tab<<tr(td(span(case_name,style='color:black;font-size:15px;')) + td('NULL') + td(span(a('premitive file', target='_blank', href=file_path))))
            else:
                tab<<tr(td(span(case_name,style='color:black;font-size:15px;')) + td('NULL') + td(span(a('premitive file', target='_blank', href=file_path))))
        else:
            if not page:
                page = PyH('result')
                page<<br()<<br()
                page<<div(b('升级后存在，升级前不存在的信令',style='font-size:18px'))
                tab = page<<table(border='2')
                tab<<tr(th('before') + th('after'))
                tab<<tr(td('NULL') + td(span(case_name,style='color:black;font-size:15px;')) + td(span(a('premitive file', target='_blank', href=file_path))))
            else:
                tab<<tr(td('NULL') + td(span(case_name,style='color:black;font-size:15px;')) + td(span(a('premitive file', target='_blank', href=file_path))))
        return page,tab

def compare(xml_dict, Filenames, params_dict, file_number_list,page_dict,sequence):
    for a in file_number_list:
        id = Filenames[a].split('@')[0]
        case_name = Filenames[a].split('.')[0].decode('gbk')
        file_path = '{1}\\{0}.html'.format(id,params_dict['output_path'])
        fullfilename1 = os.path.join(params_dict['dir_path0'],Filenames[a])
        fullfilename2 = os.path.join(params_dict['dir_path1'],Filenames[a])
        dict1, compare_dict1, content1 = Test.read_txt_file(xml_dict,fullfilename1,params_dict['just_compare_send'])
        dict2, compare_dict2, content2 = Test.read_txt_file(xml_dict,fullfilename2,params_dict['just_compare_send'])
        Test.premitive_file(content1,content2,file_path)
        is_current_case_over = 0
        if dict1 and dict2 and len(dict1)<=len(dict2):
            dict2_index = dict2.keys()   #升级后消息的序号
            for i in dict1.iterkeys():
                m=0        #dict_index中元素的索引
                # n=dict2_index[m]        #消息序号
                # k=n-i      #序号差值，用于设置门限
                level2_before = [params for params in compare_dict1[i][1] if isinstance(params,str)]
                level2_after = [params for params in compare_dict2[i][1] if isinstance(params,str)]
                if not i in dict2_index or not dict1[i].split(':')[0]==dict2[i].split(':')[0] or level2_before!=level2_after:
                    while not dict1[i].split(':')[0]==dict2[dict2_index[m]].split(':')[0] or not level2_before==[params for params in compare_dict2[dict2_index[m]][1] if isinstance(params,str)]:
                        m+=1
                        if m==len(dict2_index) or dict2_index[m]-i>13:
                            break
                    if m<len(dict2_index):
                        n = dict2_index[m]
                else:
                    n = i
                if m==len(dict2_index) or dict2_index[m]-i>13:
                    if not a or file_number_list[0] == a:
                        if not is_current_case_over:
                            page,tab = Test.create_page(file_path,a+1,case_name,None,None,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                            # Test.premitive_file(content1,None,file_path,1)
                        else:
                            page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                    elif is_current_case_over:
                        page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                    else:
                        page,tab = Test.create_page(file_path,a+1,case_name,page,None,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                    is_current_case_over+=1
                    continue
                else:
                    dict2_index.remove(n)
                diff_list = list_compare(compare_dict1[i][1],compare_dict2[n][1],[])
                for index in range(0,len(diff_list),2):
                    if not a or file_number_list[0] == a:   # a = 0时，即第一条用例
                        if not is_current_case_over:         #第一条差异
                            page,tab = Test.create_page(file_path, a+1,case_name,None,None,dict1[i],diff_list[index],diff_list[index+1], is_current_case_over)
                        else:
                            page,tab = Test.create_page(file_path, a+1,case_name,page,tab,dict1[i],diff_list[index],diff_list[index+1], is_current_case_over)
                    elif is_current_case_over:
                        page,tab = Test.create_page(file_path, a+1,case_name,page,tab,dict1[i],diff_list[index],diff_list[index+1], is_current_case_over)
                    else:
                        page,tab = Test.create_page(file_path, a+1,case_name,page,None, dict1[i],diff_list[index],diff_list[index+1],is_current_case_over)
                    is_current_case_over+=1
            # if dict2_index:
            for i in dict2_index:
                if not a or file_number_list[0] == a:
                    if not is_current_case_over:
                        page,tab = Test.create_page(file_path,a+1,case_name,None,None,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)
                    else:
                        page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)                           
                else:
                    page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)
                is_current_case_over+=1
            if not is_current_case_over:
                if not a or file_number_list[0] == a:
                    page,tab = Test.create_page(file_path, a+1,case_name)
                else:
                    page,tab = Test.create_page(file_path, a+1,case_name,page)
        elif not dict1 and not dict2 and not compare_dict1 and not compare_dict2:
            if not a or file_number_list[0] == a:
                page,tab = Test.create_page(file_path,a+1,case_name,None,None,u'升级前后文件内容都为空:',None,None)
            else:
                page,tab = Test.create_page(file_path,a+1,case_name,page,None,u'升级前后文件内容都为空:',None,None)
        elif not dict1 and not compare_dict1:
            if not a or file_number_list[0] == a:
                page,tab = Test.create_page(file_path,a+1,case_name,None,None,u'升级前后一个文件内容为空:',None,u'升级前文件内容为空')
            else:
                page,tab = Test.create_page(file_path,a+1,case_name,page,None,u'升级前后一个文件内容为空:',None,u'升级前文件内容为空')
        elif not dict2 and not compare_dict2:
            if not a or file_number_list[0] == a:
                page,tab = Test.create_page(file_path,a+1,case_name,None,None,u'升级前后一个文件内容为空:',u'升级后文件内容为空',None)
            else:
                page,tab = Test.create_page(file_path,a+1,case_name,page,None,u'升级前后一个文件内容为空:',u'升级后文件内容为空',None)
        else:
            dict1_index = dict1.keys()
            for i in dict2.iterkeys():
                level2_before = [params for params in compare_dict1[i][1] if isinstance(params,str)]
                level2_after = [params for params in compare_dict2[i][1] if isinstance(params,str)]
                m=0
                if not i in dict1_index or not dict2[i].split(':')[0]==dict1[i].split(':')[0] or level2_before!=level2_after:
                    while not dict2[i].split(':')[0]==dict1[dict1_index[m]].split(':')[0] or not level2_after==[params for params in compare_dict1[dict1_index[m]][1] if isinstance(params,str)]:
                        m+=1
                        if m==len(dict1_index) or dict1_index[m]-i>13:
                            break
                    if m<len(dict1_index):
                        n = dict1_index[m]
                else:
                    n = i
                if m==len(dict1_index) or dict1_index[m]-i>13:
                    if not a or file_number_list[0] == a:
                        if not is_current_case_over:
                            page,tab = Test.create_page(file_path,a+1,case_name,None,None,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)
                        else:
                            page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)
                    elif is_current_case_over:
                        page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)
                    else:
                        page,tab = Test.create_page(file_path,a+1,case_name,page,None,dict2[i],None,u'升级前不存在此消息 ',is_current_case_over)
                    is_current_case_over+=1
                    continue
                else:
                    dict1_index.remove(n)
                diff_list = list_compare(compare_dict1[n][1],compare_dict2[i][1],[])
                # if diff_list:
                for index in range(0,len(diff_list),2):
                    if not a or file_number_list[0] == a:   # a = 0时，即第一条用例
                        if not is_current_case_over:         #第一条差异
                            page,tab = Test.create_page(file_path, a+1,case_name,None,None,dict1[i],diff_list[index],diff_list[index+1], is_current_case_over)
                        else:
                            page,tab = Test.create_page(file_path, a+1,case_name,page,tab,dict1[i],diff_list[index],diff_list[index+1], is_current_case_over)
                    elif is_current_case_over:
                        page,tab = Test.create_page(file_path, a+1,case_name,page,tab,dict1[i],diff_list[index],diff_list[index+1], is_current_case_over)
                    else:
                        page,tab = Test.create_page(file_path, a+1,case_name,page,None, dict1[i],diff_list[index],diff_list[index+1],is_current_case_over)
                    is_current_case_over+=1
            # if dict1_index:
            for i in dict1_index:
                if not a or file_number_list[0] == a:
                    if not is_current_case_over:
                        page,tab = Test.create_page(file_path,a+1,case_name,None,None,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                    else:
                        page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                else:
                    page,tab = Test.create_page(file_path,a+1,case_name,page,tab,dict1[i],u'升级后不存在此消息',None,is_current_case_over)
                is_current_case_over+=1
            if not is_current_case_over:
                if not a or file_number_list[0] == a:
                    page,tab = Test.create_page(file_path, a+1,case_name)
                else:
                    page,tab = Test.create_page(file_path, a+1,case_name,page)
    page_dict[sequence] = page

def list_compare(before,after,diff_list):
    if before == after: return diff_list
    before_left=[]
    for index,value in enumerate(before):
        if isinstance(value,str):
            if value in after:
                if index < len(before)-1:                   
                    if isinstance(before[index+1],list):
                        if after.index(value) < len(after)-1 and isinstance(after[after.index(value)+1],list):
                            diff_list = list_compare(before[index+1],after[after.index(value)+1],diff_list)
                            after.remove(after[after.index(value)+1])
                        else:
                            diff_list.append(u'升级前 '+ value + u' 内不为空')
                            diff_list.append(u'升级后为空')
                    elif after.index(value) < len(after)-1 and isinstance(after[after.index(value)+1],list):
                        diff_list.append(u'升级前为空')
                        diff_list.append(u'升级后 '+ value + u' 内不为空')
                elif after.index(value) < len(after)-1 and isinstance(after[after.index(value)+1],list):
                    diff_list.append(u'升级前为空')
                    diff_list.append(u'升级后 '+ value + u' 内不为空')
                after.remove(value)
            else:
                if index < len(before)-1 and isinstance(before[index+1],list): 
                    diff_list.append(value)
                    diff_list.append(u'升级后没有该字段')
                elif ':' in value:
                    before_left.append(value)
                else:
                    diff_list.append(value)
                    diff_list.append(u'升级后没有该字段')
    after_remove_list=[]
    for index,value in enumerate(before_left):
        if value.split(':')[0] in [params.split(':')[0] for params in after if isinstance(params,str)]:
            for item in after:
                if isinstance(item,str) and value.split(':')[0] in item:
                    diff_list.append(value)
                    diff_list.append(item)
                    after_remove_list.append(item)
                    break
        else:
            diff_list.append(value)
            diff_list.append(u'升级后没有该字段')
    for item in after_remove_list:
        after.remove(item)
    for item in after:
        if isinstance(item,str):
            diff_list.append(u'升级前不存在该字段')
            diff_list.append(item)

    return diff_list
#字符串相似度算法
    # @staticmethod
    # def levenshtein(first,second):
    #     if len(first) > len(second):
    #         first,second = second,first
    #     if len(first) == 0:
    #         return len(second)
    #     if len(second) == 0:
    #         return len(first)
    #     first_length = len(first) + 1
    #     second_length = len(second) + 1
    #     distance_matrix = [range(second_length) for x in range(first_length)]
    #     for i in range(1,first_length):
    #         for j in range(1,second_length):
    #             deletion = distance_matrix[i-1][j] + 1
    #             insertion = distance_matrix[i][j-1] + 1
    #             substitution = distance_matrix[i-1][j-1]
    #             if first[i-1] != second[j-1]:
    #                 substitution += 1
    #             distance_matrix[i][j] = min(insertion,deletion,substitution)
    #     return distance_matrix[first_length-1][second_length-1] / second_length
if __name__ == '__main__':
    # args = sys.argv[1:]
    # test = Test(args)
    test = Test(['C:\\Users\\6407001091\\Desktop', 'E:\\umac_local\\filters', '1'])
    test.main()

