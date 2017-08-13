# -*- coding: utf-8 -*-

## set the file encoding as utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import re
from robot.api import logger
import time
import logging

class umacHtml:
    # 定义基本属性
    html = ''

    # 定义构造方法
    def __init__(self, n):
        self.html = n
        self.dbLog = logging.getLogger('umacHtmlMain.umacHtml')

    def umacHtmlSplit(self, cmd, ver):
        if self.html.find(cmd) == -1:
            logger.info('No found command {0}'.format(cmd))
            return None

        str1 = cmd + self.html.split(cmd)[1]

        if str1.find(cmd + '</b><br>') != -1:
            begin = cmd + '</b><br>'
        elif str1.find(cmd + '<br>') != -1:
            begin = cmd + '<br>'
        else:
            logger.warn('error command {0}'.format(str1))

        if ver == 0:
            end = 'Executed command'
        elif ver == 1:
            end = u'命令执行'
        else:
            logger.warn('invalid version:{0}'.format(ver))

        return str1.split(begin)[1].split(end)[0]

    def umacHtmlParase(self, strTable):
        listResult = []
        soup = BeautifulSoup(strTable)
        foundCmnTable = soup.find('table')
        if not foundCmnTable:
            #self.dbLog.info('not found table:{0}'.format(strTable))
            return
        strTable = strTable.replace("&nbsp;", "")
        td_complie = re.compile('<TD .*?>(.*?)</TD>', re.I)
        tr_result = re.findall('<TR>(.*?)</TR>', strTable, re.I)
        if not tr_result:
            return listResult

        for tr in tr_result:
            td_result = td_complie.findall(tr)
            if not td_result:
                continue
            listResult.append(td_result)

        return listResult
        # foundAllTr = foundCmnTable.findAll("tr")


        # def umacHtmlParase(self, strTable):
        #     time.sleep(0.05)
        #     listResult = []
        #     soup = BeautifulSoup(strTable)
        #     foundCmnTable = soup.find('table')
        #     # if 'Number of identity request retransmission' in strTable:
        #     #     with open('c:/aaa.txt','w') as f:
        #     #         f.write(strTable)
        #     if (foundCmnTable):
        #         foundAllTr = foundCmnTable.findAll("tr")
        #     else:
        #         logger.warn('not found table:{0}'.format(strTable))
        #         return
        #     if (foundAllTr):
        #         for tr in foundAllTr:
        #             foundAllTd = tr.findAll("td")
        #             if (foundAllTd):
        #                 listTemp = []
        #                 for td in foundAllTd:
        #                     listTemp.append(td.get_text())
        #                 listResult.append(listTemp)
        #             else:
        #                 print "No found TD!"
        #     else:
        #         print "No found TR!"
        #         return
        #     return listResult

        # -------------------------------------------------------------------------------

    # Name:         get_cmd_Content
    # 入参：         命令名称
    # 返回值：       返回命令名称对应的命令体（HTML格式），否则返回None
    # Purpose:      根据命令名称解析命令体
    #
    # Author:      印骅
    #
    # Created:     27-03-2015
    # Modified：   15-04-2015
    # -------------------------------------------------------------------------------
    def get_cmd_content(self, cmdname):
        regexp = r'\b' + cmdname + r'\b'
        prog = re.compile(regexp, re.I)

        if not prog.search(self.html):
            return None

        regexp = cmdname + r'(</b><br>|<br>)(.*?)(Executed command|命令执行)'
        # 20150415 yh 添加查询模式为UNICODE，支持中文查询
        prog = re.compile(regexp, re.UNICODE | re.S | re.I)

        if not prog.search(self.html):
            return None

        return prog.search(self.html).group(2)

        # -------------------------------------------------------------------------------

    # Name:         getAllCmdName
    # 入参：         无
    # 返回值：       返回html源码中所有命令名称组成的列表，否则返回None
    # Purpose:      获取html源码中所有命令名称
    #
    # Author:      印骅
    #
    # Created:     15-04-2015
    # Modified：   15-04-2015
    # -------------------------------------------------------------------------------
    def getAllCmdName(self):
        lstAllRst = []
        lstAllCmdName = []

        regexp = "(command|命令) \(no.\d{1,3}\):(.*?)(</b><br>|<br>)"
        prog = re.compile(regexp, re.UNICODE | re.I)
        lstAllRst = prog.findall(self.html)

        for k in lstAllRst:
            lstAllCmdName.append(k[1])

        # 20150422 yh 去除重复元素
        lstAllCmdName = list(set(lstAllCmdName))

        return lstAllCmdName

    # 20150506 yh 同时返回所有命令名称及其对应的命令内容，get_cmd_content和getAllCmdName函数废弃
    def getAllCmdNameAndContent(self):
        # regexp="command \(no\.\d{1,4}\):(.*?)(</b><br>|<br>)(.*?)\(elapsed"
        # 20150521 yh 支持中文
        regexp = "(command|命令) \(no\.\d{1,4}\):(.*?)(</b><br>|<br>)(.*?)(elapsed|耗时)"
        prog = re.compile(regexp, re.UNICODE | re.S | re.I)

        lstRet = prog.findall(self.html)

        # 删除列表中不包含<table的元素
        idx = 0
        while idx < len(lstRet):
            if not '<table' in lstRet[idx][3].lower():
                del lstRet[idx]
            else:
                idx += 1

        return lstRet

    # 20150528 yh 判断网元类型，返回对应的cfg命令
    def get_showCFGCmdName(self):
        combocfg = r'\bSHOW COMBOCFG\b'
        sgsncfg = r'\bSHOW SGSNCFG\b'
        mmecfg = r'\bSHOW MMECFG\b'

        prog = re.compile(combocfg, re.I)
        if prog.search(self.html):
            return combocfg

        prog = re.compile(sgsncfg, re.I)
        if prog.search(self.html):
            return sgsncfg

        prog = re.compile(mmecfg, re.I)
        if prog.search(self.html):
            return mmecfg

        return None


if __name__ == "__main__":
    html = """<HEAD><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><TITLE>Terminal exported data</TITLE></HEAD><B>Command (No.1):</B> SHOW DEFAULT VOICESET POLICY<br>
<br>
<table border="1" cellpadding="3" bordercolorlight="#999999" bordercolordark="#FFFFFF" cellspacing="0" style="font-size:14;font-family:Lucida Console"><tbody>
<tr><td noWrap>Maintenance</td><td noWrap>Additional&nbsp;Update&nbsp;Result</td><td noWrap>IMS&nbsp;VoPS</td><td noWrap>User&nbsp;Alias</td></tr>
<tr><td noWrap><U>Modify</U>&nbsp;</td><td noWrap>no&nbsp;additional&nbsp;information</td><td noWrap>Support</td><td noWrap>yyyy</td></tr>
</tbody></table><br><B>1 Record(s)</B><br>
<br>
<B>Executed command successful (elapsed 0.048s).</B><br>
<br>
<br>
<B>Command (No.2):</B> SHOW DEFAULT RFSP<br>
<br>
<table border="1" cellpadding="3" bordercolorlight="#999999" bordercolordark="#FFFFFF" cellspacing="0" style="font-size:14;font-family:Lucida Console"><tbody>
<tr><td noWrap>Maintenance</td><td noWrap>Policy&nbsp;Control</td><td noWrap>RFSP&nbsp;Index</td><td noWrap>User&nbsp;Alias</td></tr>
<tr><td noWrap><U>Modify</U>&nbsp;</td><td noWrap>Local&nbsp;Configuration&nbsp;Preferred</td><td noWrap>0</td><td noWrap></td></tr>
</tbody></table><br><B>1 Record(s)</B><br>
<br>
<B>Executed command successful (elapsed 0.032s).</B><br>
<br>
<br>
<B>Command (No.3):</B> SHOW MME ODB<br>
<br>
<table border="1" cellpadding="3" bordercolorlight="#999999" bordercolordark="#FFFFFF" cellspacing="0" style="font-size:14;font-family:Lucida Console"><tbody>
<tr><td noWrap>Maintenance</td><td noWrap>Barring&nbsp;of&nbsp;All&nbsp;PS&nbsp;Services</td><td noWrap>Forbids&nbsp;to&nbsp;Visit&nbsp;HPLMN&nbsp;APN</td><td noWrap>Forbids&nbsp;to&nbsp;Visit&nbsp;VPLMN&nbsp;APN</td></tr>
<tr><td noWrap><U>Modify</U>&nbsp;</td><td noWrap>NO</td><td noWrap>NO</td><td noWrap>NO</td></tr>
</tbody></table><br><B>1 Record(s)</B><br>
<br>
<B>Executed command successful (elapsed 0.032s).</B>"""

    # #印骅测试
    # f = open(r'D:\customtool\data\BR_20150518141820.html')
    # #htmlData = f.read().encode('utf-8')
    # htmlData = f.read()
    # f.close()
    #
    # umac=umacHtml(htmlData)

    with open('c:/bbb.txt', 'r') as f:
        s = f.read()

    u = umacHtml('')
    ls = u.umacHtmlParase(s)
    print str(ls)
    #    umac.getAllCmdName()
    #    umac.get_cmd_content("show sgsncfg")

    ##    from time import clock
    ##    start=clock()
    # lstTest = umac.getAllCmdNameAndContent()
    ##    finish=clock()
    ##    print finish-start
    pass


##    print html
##    f = open('umac.html')
##    htmlData = f.read()
##    f.close()
##    print htmlData
##
##    umacH = umacHtml(htmlData)
##    s = umacH.umacHtmlSplit('SHOW SOFTWARE PARAMETER')
##    print "==eeeeeeee"
##    listR = umacH.umacHtmlParase(s)
##    if(listR):
##        for x in listR:
##            y = x
##            print ''
##            for s in y:
##                print s,
