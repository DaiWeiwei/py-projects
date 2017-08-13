# coding:utf-8
import xlrd
import os
import re
import time
import sys
from robot.api import logger
class umaclicensetest(object):
    #查询license
    @staticmethod
    def run_get_license(umac_dut,umac_lang='cn'):
        licenselist=[]
        valid_date=[]
        try:
            cmd = 'SHOW LICENSE;'
            cmd_result = umac_dut.execute_command(cmd)
            context=cmd_result.return_string
            if context.find('&')==-1:
                logger.info(u"网管服务器上没有对应License文件，请先上传license文件！")
                return licenselist,valid_date
            context1=context.split('&')  #以&对结果进行截取
            alllen=len(context1)
            valid_date=re.findall('(\"\d+\-\d+\-\d+\"\-\"\d+\-\d+\-\d+\")',context1[0])
            beg_len= context1[0].index('ITEMINFO=') #查找结果返回的第一个记录的开始符位置
            context1[0]=context1[0][beg_len+len('ITEMINFO='):] #更新第一个记录内容
            en_len=context1[alllen-1].index(',SYS_RESULT=') #查找最后一个记录的结束符位置
            context1[alllen-1]=context1[alllen-1][:en_len]  #更新最后一条记录
           # 取功能项和值写到license列表中
            for i in  range(alllen):
                aa=context1[i].split('"-"')[0].replace('"','')
##                if aa==u'MME是否支持签约通配的APN更正'.decode('utf-8') :
##                    aa=u'MME支持签约通配的APN更正功能'.encode('utf-8')
                licenselist.append(aa+','+context1[i].split('"-"')[2].replace('"',''))
##            for i in  range(alllen):
##                print licenselist[i]
            if not result:
               raise Exception("cannot get license!")
               return licenselist,valid_date
        except:
            return licenselist,valid_date

        #激活license文件
    @staticmethod
    def run_active_license(umac_dut):
        try:
            cmd = 'LOAD LICENSE;'
            cmd_result = umac_dut.execute_command(cmd)
        except:
            logger.info(u'激活失败')
            pass

        #获取license申请表中的网元属性和申请表的中英文信息和所属位置
    @staticmethod
    def get_license_appinfo(file,by_index=2):
         reload(sys)
         sys.setdefaultencoding('utf-8')
         license_apply=[]
         license_info={}
         data = xlrd.open_workbook(file)
         count = len(data.sheets())
         if count<2:
            raise Exception("当前申请表中没有申请内容，请检查申请表")

         if count<by_index+1:
            raise Exception("当前输入的sheet索引大于实际申请表中sheet索引")


         table = data.sheets()[by_index]#data.sheet_by_name(by_name)
         nrows=0
         ncols=0
         nrows = table.nrows #行数
         ncols = table.ncols-1  #列数
         ne_row=0
         ne_col=0


#定位网元类型 ，找到记录行列后就退出
         for row in range(nrows):
            for col in range(ncols):
                if table.cell(row,col).value=='NE type' :    #先找到网元类型的位置
                    user_num=table.cell(row+1,col+1).value
                    if type(user_num) is float or type(user_num) is int: #再判断下一行的注册用户数是否填写，如果填写则就是正确的位置
                        license_info['Lange']='EN'
                        license_info['Netype']=table.cell(row,col+1).value.strip()
                        license_info['Version']=table.cell(row-2,col+1).value.strip()
                        ne_row=row
                        ne_col=col
    ##                    logger.info(ne_row)
                        break

                if table.cell(row,col).value=='网元类型'.decode('utf-8') :
                    user_num=table.cell(row+1,col+1).value
                    if type(user_num) is float or type(user_num) is int:
                        license_info['Lange']='CN'
                        license_info['Netype']=table.cell(row,col+1).value.strip()
                        license_info['Version']=table.cell(row-2,col+1).value.strip()
                        ne_row=row
                        ne_col=col
                        break



#定位各个功能项内容，写入字典
         for i in range(ne_row+1,nrows):
            if table.cell(i,ne_col-1).value.strip()==u'填写人' or table.cell(i,ne_col-1).value.strip()=='Written by':   #这个是兼容申请表填写在OMM-License模板这个sheet中，防止读取后面的空模板
                break
            if table.cell(i,ne_col).value:
##                logger.info(i)
                aa=table.cell(i,ne_col+1).value
                if type(aa) is float or type(aa) is int:
                    aa=str(int(aa))
                else :
                    if aa[:3]==u'■ON':
                        aa='ON'
                    else :
                        aa='OFF'
                bb=table.cell(i,ne_col).value.strip()
                if bb==u'MME支持eNB用户面IP地址类型优选功能':
                    bb=u'MME支持eNB用户面IP地址类型优选'
                if bb=='MME Support SGs Association Restoration' :
                    bb='MME Support SGs Association initiative Restoration'
                if 'MBR(Mbps)' in bb or 'GBR(Mbps)' in bb:
                    if aa=='OFF':
                        aa='256'
                if 'LCS Number' in bb  or u'LCS用户数' in bb:
                    if aa=='OFF':
                        aa='1'
                license_apply.append(bb+','+aa)

         return license_apply, license_info
#对比license文件和申请表中内存，检查有无差异
    @staticmethod
    def compare_license_info(umac_dut,license_apply,license_info):

#激活license文件

      umaclicensetest.run_active_license(umac_dut)
#获取license 文件信息
      license_file=[]
      valid_data=[]
      license_file,valid_data=umaclicensetest.run_get_license(umac_dut)
      if len(license_file)==0:
        logger.info(u'License文件没有激活成功！')
        return


      logger.info(u'****************License 文件内容如下：*********************')
      for i in range(len(license_file)):
         logger.info(license_file[i].decode('utf-8'))
#获取license申请表信息

      license_change=[]
      license_result=[]
      license_change=umaclicensetest.license_lang_change(license_file,license_info['Lange'])


      for i in license_change:
            if i not in license_apply:
                license_result.append(u'License 文件中：  '+i)

      for j in license_apply:
            if j not in license_change:
                license_result.append(u'License 申请表中：'+j)


      logger.info('****************License 申请表文件内容如下：****************')
      for i in range(len(license_apply)):
         logger.info(license_apply[i])
      logger.info('######################################验证结果如下######################################')
      logger.info('#######################License有效期为：'+valid_data[0]+'#######################')
      logger.info('############################ 网  元  类  型  为：'+license_info['Netype']+'  ##################################')


      if len(license_result)>0:
        logger.info('很遗憾！License申请或者制作有问题，差异如下：')
        for k in range(len(license_result)):
             logger.info('验证结果：  '+license_result[k])
      else :
        logger.info('恭喜您！License文件和申请表中的内容一致，验证通过！  ')




#将license文件中语言类别转换成和申请表中的一致
    @staticmethod
    def license_lang_change(source,lang='CN'):

            #创建license功能项中英文对照表
      license_cntoen={
        '注册用户数':'Register User Number',
        '2G注册用户数':'2G Register User Number',
        '3G注册用户数':'3G Register User Number',
        'LTE注册用户数':'LTE Register User Number',
        '在线用户数':'Online User Number',
        '2G在线用户数':'2G Online User Number',
        '3G在线用户数':'3G Online User Number',
        'LTE在线用户数':'LTE Online User Number',
        '本局承载/PDP上下文最大数':'Max Bearer/PDP Context Number',
        '动态eNodeB容量':'Max Dynamic eNodeB Number',
        'SGSN支持LCS用户数':'SGSN Support LCS Number',
        'MME支持LCS用户数':'MME Support LCS Number',
        'SGSN支持的上行MBR(Mbps)':'MBR for Uplink of SGSN Supporting(Mbps)',
        'SGSN支持的下行MBR(Mbps)':'MBR for Downlink of SGSN Supporting(Mbps)',
        'SGSN支持的上行GBR(Mbps)':'GBR for Uplink of SGSN Supporting(Mbps)',
        'SGSN支持的下行GBR(Mbps)':'GBR for Downlink of SGSN Supporting(Mbps)',
        '单模块最大IWS用户数':'Maximum IWS Users by Single Module',
        '支持UBAS-CHR功能':'Support UBAS-CHR Function',
        'GnGp SGSN支持MOCN功能':'GnGp SGSN Support MOCN Function',
        'SGSN支持DT功能':'SGSN Support Direct Tunnel Function',
        'MME支持CSFB功能':'MME Support CSFB Function',
        '支持IPv6功能':'Support IPv6 Function',
        'MME支持SRVCC功能':'MME Support SRVCC Function',
        'MME支持CSG功能':'MME Support CSG Function',
        'MME支持eMBMS功能':'MME Support eMBMS Function',
        'MME支持NITZ功能':'MME Support NITZ Function',
        'MME支持IPSEC功能':'MME Support IPSEC Function',
        '支持LCS功能':'Support LCS Function',
        'MME支持策略寻呼功能':'MME Support Policy Paging Function',
        'MME支持LIPA功能':'MME Support LIPA Function',
        'MME支持eNB用户面IP地址类型优选':'MME Support eNB User Plane IP Address Type Optimization',
        'MME支持Relay功能':'MME Support Relay Function',
        '支持用户IP地址和位置关联功能':'Support User IP and Location Relationship Function',
        'MME支持信令风暴抑制':'MME Support Signaling Storm Restraint',
        'SGSN支持大容量其他HPLMN配置':'SGSN Support Large Number of Served PLMNs',
        'MME支持TCE功能':'MME Support TCE Function',
        'SGSN支持NITZ功能':'SGSN Support NITZ Function',
        'MME支持优化切换到eHRPD功能':'MME Support Handover with Optimization to eHRPD',
        'MME支持MME容灾故障恢复功能':'MME Support Service Restoration after an MME Failure',
        'MME支持S102接口':'MME Support S102 Interface',
        'MME支持内嵌IWS功能':'MME Support IWS Function',
        'MME支持P-CSCF恢复功能':'MME Support P-CSCF Restoration Function',
        'MME支持S3接口':'MME Support S3 Interface',
        'MME支持SGs口主动恢复':'MME Support SGs Association initiative Restoration',
        'MME支持SGW容灾故障恢复功能':'MME Support Service Restoration after an SGW Failure',
        'MME支持PGW容灾故障恢复功能':'MME Support Service Restoration after an PGW Failure',
        'MME支持PLMN测量功能':'MME Support PLMN Measurement Function',
        'MME支持TA测量统计数量':'MME Support TA Measurement Configuration',
        'MME支持APN测量功能':'MME Support APN Measurement Function',
        'MME支持QCI测量功能':'MME Support QCI Measurement Function',
        'MME支持域测量功能':'MME Support Area Measurement Function',
        'MME支持APN接入控制功能':'MME Support APN Access Control',
        'MME支持签约通配的APN更正功能':'MME Support APN Modification for Subscribe Wildcard Function',
        'SGSN支持将UE选择的PLMN带给GGSN功能':'SGSN Support Sending the PLMN Selected by UE to GGSN Function',
        'MME支持MPS功能':'MME Support MPS Function',
        'SGSN支持IMEI Check携带用户IMSI和MSISDN':'SGSN Support IMEI Check with IMSI and MSISDN',
        'MME支持PGW的APN拥塞功能':'MME Support PGW APN Congestion Function',
        'MME支持PGW重选功能':'MME Support PGW Reselection Function',
        'MME支持TAL静态分配功能':'MME Support TAL Statically Configuration Function',
        'HSS过负荷控制功能':'HSS Overload Control Configuration Function',
        'MME支持基于APN拥塞控制功能':'MME Support Congestion Control Based on APN Function',
        'MME支持基于MTC用户拥塞控制功能':'MME Support Congestion Control Based on MTC Subscriber Function',
        'MME支持GTP-C负荷控制功能':'MME Support GTP-C Load Control Function',
        'MME支持GTP-C过负荷控制功能':'MME Support GTP-C Overload Control Function',
        'MME支持直接向UE获取IMSI功能':'MME Support getting IMSI from UE directly',
        '支持GTP节点白名单':'Support GTP Node White List',
        'SGSN支持寻呼缓存控制功能':'SGSN Support Buffer Paging Control Function',
        'MME支持双连接功能':'MME Support Dual Connectivity Function',
        'MME支持PRA功能':'MME Support PRA Function',
        'MME支持用户QoS控制':'MME supports user QoS control',
        'MME支持容灾故障恢复功能':'MME Service Restoration Function',
        'MME支持APN拥塞功能':'MME Support APN Congestion Function',
        'MME支持跟踪Cell Traffic Trace消息的eNB数':'Number of eNB allowed to report Cell Traffic Trace message'

         }

     #创建英文-中文对照字典
      license_entocn=dict([ (v, k) for k, v in license_cntoen.iteritems( ) ])
     #确认license文件中的中英文信息，实际网管服务器的中英文信息。
      license_files=source
      licensefile_lang=''
      licenseapp_lang=lang
      license_usernum=license_files[0].split(',')[0]
      if license_cntoen.has_key(license_usernum):
        licensefile_lang='CN'
      else:
        licensefile_lang='EN'

      #如果申请文件中语言和网管的一致，则直接返回
      if licensefile_lang==licenseapp_lang :
        return license_files
      if licensefile_lang=='CN' and licenseapp_lang=='EN' :
          for i in range(len(license_files)):
            function_name=license_files[i].split(',')[0]
            if function_name==u'MME是否支持签约通配的APN更正' :
                function_name=u'MME支持签约通配的APN更正功能'.encode('utf-8')

            if not license_cntoen.has_key(function_name) :
                 logger.info('中文LICENSE文件中的功能名称和字典不一致，license文件中：'+function_name)
            license_files[i]=license_cntoen[function_name]+','+license_files[i].split(',')[1]
      if licensefile_lang=='EN' and licenseapp_lang=='CN' :

        for i in range(len(license_files)):
            function_name=license_files[i].split(',')[0]
            if function_name=='MME Support SGs Association Restoration':
                function_name='MME Support SGs Association initiative Restoration'
            if function_name=='MME Support APN Modification for Subscribe Wildcard':
                function_name='MME Support APN Modification for Subscribe Wildcard Function'
            if not license_entocn.has_key(function_name) :
                logger.info('英文LICENSE文件中的功能名称和字典不一致，license文件中：'+function_name)

            license_files[i]=license_entocn[function_name]+','+license_files[i].split(',')[1]
      return license_files


















if __name__=="__main__":
     file=''