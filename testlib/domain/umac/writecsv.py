# -*- coding: gbk -*-


import umacHtml
import csv
import os
import codecs

#-------------------------------------------------------------------------------
# Name:         opercsv
#��Σ�         һά�б�
#����ֵ��       ��
# Purpose:      ��һά�б�ֵд��csv��
#
# Author:      ��ΰ
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
#���1��        ����������ɵ��б�
#���2��        ���ID
#���3��        �������ֵ
#����ֵ��       �Ƿ�һ�£�0-һ�£�1-��һ�£�2-�Ҳ���
# Purpose:      �ж�ĳ���ֵ�Ƿ���Ԥ��һ��
#
# Author:      ��ΰ
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

    listR = ['����','����','����','ֵ']
    opercsv(listR)




