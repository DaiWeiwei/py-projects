# -*- coding: gbk -*-


import umacHtml
import csv
import os
import codecs

#-------------------------------------------------------------------------------
# Name:         opercsv
#入参：         一维列表
#返回值：       无
# Purpose:      将一维列表值写入csv中
#
# Author:      李伟
#
# Created:     27-03-2015
#-------------------------------------------------------------------------------
def opercsv(listR):
    dstpath = r'F:\Python\xuqiu\Test1.csv'
    j = 0
    if os.path.exists(dstpath):
        file1 = open(dstpath)
        reader = csv.reader(file1)
        row_list = []
        for i in reader:
            row_list.append(i)
            #print row_list
            j = j + 1
        file1.close()
        #print j

    csfile = file(dstpath,'wb')
    write = csv.writer(csfile)
    if j > 0:
        for i in range(0,j):
            d = row_list[i]
            #print i,d
            write.writerows([(row_list[i])])
    write.writerows([(listR)])
    csfile.close()

#-------------------------------------------------------------------------------
# Name:         IsSupportSoft
#入参1：        所有软参生成的列表
#入参2：        软参ID
#入参3：        软参期望值
#返回值：       是否一致，0-一致，1-不一致，2-找不到
# Purpose:      判断某软参值是否与预期一致
#
# Author:      李伟
#
# Created:     27-03-2015
#-------------------------------------------------------------------------------
def IsSupportSoft(listR, softid, value):
    flag = 2
    for i in listR:
        if i[1] == str(softid):
            flag = 1
            #for j in i:
            #    print j
            if i[3] == str(value):
                flag = 0
    return flag

if __name__=="__main__":

    f = open('umac.html')
    htmlData = f.read()
    f.close()

    umacH = umacHtml.umacHtml(htmlData)
    s = umacH.umacHtmlSplit('SHOW SOFTWARE PARAMETER')
    print "==eeeeeeee"
    listR = umacH.umacHtmlParase(s)
    a = IsSupportSoft(listR, 786623, 1)
    print a

    listR = ['功能','命令','参数','值']
    opercsv(listR)




