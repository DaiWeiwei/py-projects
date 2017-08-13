# coding=utf-8
import re
import os
import time
from robot.api import logger
from testlib.infrastructure.device.umac.umacthread import UmacThread


class umacBoardstatusinfo(object):
    #OMP下电
    @staticmethod
    def get_omp_poweroff(umac_dut,omp):
        cmd='BOARD EPOWER ONOFF:CMMID='+omp['ECMM']+',SLOT='+omp['S'].split('-')[2]+',OPT="POWEROFF";'
        cmd_result = umac_dut.execute_command(cmd)
        logger.info(cmd)

    #OMP上电
    @staticmethod
    def get_omp_poweron(umac_dut,omp):
        result=-1
        cmd='BOARD EPOWER ONOFF:CMMID='+omp['ECMM']+',SLOT='+omp['S'].split('-')[2]+',OPT="POWERON";'
        cmd_result = umac_dut.execute_command(cmd)
        logger.info(cmd)
        context=cmd_result.return_string
        result=context.find('SYS_ERRMSG')
        return result

    #OMP倒换前状态查询
    @staticmethod
    def get_omp_st(umac_dut,omp):
        state=False
        count=0
        while state!=True :
            count=count+1
            cmd ='SHOW BOARDSTATE:RACK='+omp['S'].split('-')[0]+',SHELF='+omp['S'].split('-')[1]+',SLOT='+omp['S'].split('-')[2]+';'
            cmd_result = umac_dut.execute_command(cmd)
            cmd_rt=re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"',cmd_result.return_string)
            for status in cmd_rt:
                logger.info(status[3])
                if status[3] in ('1','2','254') :
                    state=True
            time.sleep(10)
            if count==50:
                state=True
                break
        return state

    #OMP倒换
    @staticmethod
    def get_omp_swp(umac_dut,omp):
        logger.info(u'OMP开始倒换！')
##        SWP NORMAL:LOC=1-2-10-1-0;
        cmd='SWP NORMAL:LOC='+omp['M']+'-1-0;'
        cmd_result = umac_dut.execute_command(cmd)
        logger.info(u'OMP倒换完成！')

    #OMP倒换前版本查询
    @staticmethod
    def get_omp_ver(umac_dut,omp):
        cmd='SHOW RUNVERPKG:LOC='+omp['M']+'-1;'
        cmd_result = umac_dut.execute_command(cmd)
##        cmd_omp=re.findall('(\d\.\d+.\d+\.\w*\.*\w*)"-"\w*',cmd_result.return_string)  #更改为分隔符获取
        cmd_omp=cmd_result.return_string.split('"-"')[4]
        omp_ver=cmd_omp.lower()
        return omp_ver


    #获取OMP所在的ECMM的id和架框槽信息
    @staticmethod
    def get_ecmm_omp_boardinfo(umac_dut):
        ecmmlist=[]
        ompinfo={}
        cmdecmm = 'SHOW INDBOARD;' #查询ECMM

        ecmm_result = umac_dut.execute_command(cmdecmm)
        ecmmresult = re.findall('(\"\d+"-"\d+"-"\d+"-"\d+\")', ecmm_result.return_string)
        cmdomp ='SHOW MODULE:MTYPE="UOMP";'#查询OMP
        omp_result= umac_dut.execute_command(cmdomp)
        ompresult=re.findall('(\"\d+"-"\d+"-"\d+"-"\d+\")',omp_result.return_string)
        omplocation=ompresult[0].replace('"','')

   #记录和OMP同框的ECMM的ID
        for i in range(len(ecmmresult)):
##            logger.info([ecmmresult[i].replace('"','').split('-')[1]])

            if ecmmresult[i].replace('"','').split('-')[1]=='0':
                cmmm=ecmmresult[i].replace('"','').split('-')[2]+'-'+ecmmresult[i].replace('"','').split('-')[3]

                ompmm=omplocation.split('-')[0]+'-'+omplocation.split('-')[1]
                if cmmm==ompmm:
                    ompinfo['ECMM']=ecmmresult[i].replace('"','').split('-')[0]
##                    logger.info(ecmmresult[i].replace('"','').split('-')[0])
                    break
   #查询OMP状态
        cmd='SHOW BOARDSTATE:RACK='+omplocation.split('-')[0]+',SHELF='+omplocation.split('-')[1]+',SLOT='+omplocation.split('-')[2]+';'

        omp_st= umac_dut.execute_command(cmd)
        omp1_state=re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"',omp_st.return_string)

        cmd='SHOW BOARDSTATE:RACK='+omplocation.split('-')[0]+',SHELF='+omplocation.split('-')[1]+',SLOT='+omplocation.split('-')[3]+';'

        omp_st= umac_dut.execute_command(cmd)
        omp2_state=re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"',omp_st.return_string)

##        logger.info(omp_state)
        if omp1_state[0][3] not in ('1','2','254'):
           ompinfo['M']=omp2_state[0][0]+'-'+omp2_state[0][1]+'-'+omp2_state[0][2]
           ompinfo['S']=omp1_state[0][0]+'-'+omp1_state[0][1]+'-'+omp1_state[0][2]
        if omp2_state[0][3] not in ('1','2','254'):
           ompinfo['S']=omp2_state[0][0]+'-'+omp2_state[0][1]+'-'+omp2_state[0][2]
           ompinfo['M']=omp1_state[0][0]+'-'+omp1_state[0][1]+'-'+omp1_state[0][2]
        if omp1_state[0][3]  in ('1','254'):
           ompinfo['S']=omp2_state[0][0]+'-'+omp2_state[0][1]+'-'+omp2_state[0][2]
           ompinfo['M']=omp1_state[0][0]+'-'+omp1_state[0][1]+'-'+omp1_state[0][2]
        if omp2_state[0][3]  in ('1','254'):
           ompinfo['M']=omp2_state[0][0]+'-'+omp2_state[0][1]+'-'+omp2_state[0][2]
           ompinfo['S']=omp1_state[0][0]+'-'+omp1_state[0][1]+'-'+omp1_state[0][2]
        if omp1_state[0][3]  in ('2'):
           ompinfo['M']=omp2_state[0][0]+'-'+omp2_state[0][1]+'-'+omp2_state[0][2]
           ompinfo['S']=omp1_state[0][0]+'-'+omp1_state[0][1]+'-'+omp1_state[0][2]
        if omp2_state[0][3]  in ('2'):
           ompinfo['S']=omp2_state[0][0]+'-'+omp2_state[0][1]+'-'+omp2_state[0][2]
           ompinfo['M']=omp1_state[0][0]+'-'+omp1_state[0][1]+'-'+omp1_state[0][2]




 #写入字典
##        for ss in omp_state:
##            if ss[3]=='1' :
##                ompinfo['M']=ss[0]+'-'+ss[1]+'-'+ss[2]
##                ompinfo['S']=ss[0]+'-'+ss[1]+'-'+omplocation.split('-')[3]
##            if ss[3]=='2' :
##                ompinfo['M']=ss[0]+'-'+ss[1]+'-'+omplocation.split('-')[3]
##                ompinfo['S']=ss[0]+'-'+ss[1]+'-'+ss[2]
##            if  ss[3]=='254' :
##                ompinfo['M']=ss[0]+'-'+ss[1]+'-'+omplocation.split('-')[3]
##                ompinfo['S']=ss[0]+'-'+ss[1]+'-'+ss[2]
##            if  ss[3]=='0' or ss[3]=='3' :
##                pass

        return ompinfo



#获取单板状态信息
    @staticmethod
    def get_board_info(umac_dut):
        cmd = 'SHOW BOARDSTATE;'
        cmd_result = umac_dut.execute_command(cmd)
        result = re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"', cmd_result.return_string)
        if not result:
            raise Exception("cannot get board info!")

        return result
#获取正常单板信息
    @staticmethod
    def get_valid_board(result):
        board_list = []
        for board_info in result:
            #单板状态1主2备254混合态
            if board_info[4] in ('1','2','254') :
                board_list.append("{0}-{1}-{2}".format(board_info[0],board_info[1],board_info[2]))
        return board_list

#获取模块类型信息
    @staticmethod
    def get_moudle_type(umac_dut):
        boardtype_list = []
        cmd='SHOW MODULE;'
        cmd_result = umac_dut.execute_command(cmd)
        result = re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\w+)"', cmd_result.return_string)
        if not result:
            raise Exception("cannot get module info!")
        for board_info in result:
                boardtype_list.append("{0}-{1}-{2},{3}".format(board_info[0],board_info[1],board_info[2],board_info[7]))
                boardtype_list.append("{0}-{1}-{2},{3}".format(board_info[0],board_info[1],board_info[3],board_info[7]))
#去除重复的内容
        boardtype_list=list(set(boardtype_list))
        return boardtype_list
#获取单元类型信息
    @staticmethod
    def get_unit_type(umac_dut):
    #单板类型字典
        unitlist={
        '569':'UIPBEIPB2',
        '573':'UIPBEMSI',
        '10032':'USPB32E1',
        '10033':'USPB4CSTMESDHS1',
        '75569':'USPB4CSTMESDHS2',
        '197178':'UIMA32E1',
        '262714':'UIMA4CSTM1',
        '328250':'UAPB4STM1',
        '655933':'UFRB32E1',
        '721469':'UFRB4CSTM1',
        '531':'SBCO',
        '150':'GES',
        '532':'SBCW',
        '537':'SBCJ',
        '568':'FSWA1EGFS',
        '571':'BSWA0EGBS',
        '28696':'PPBC0',
        '577':'EXFS',
        '581':'EGBS2',
        '578':'EDTI2',
        '66114':'EDTI2',
        '576':'EXGB',
        '66112':'EXGB',
        '131648':'EXGB',
        '94232':'PPBC1'
        }

        unittype_list = []
        cmd='SHOW UNIT;'
        cmd_result = umac_dut.execute_command(cmd)
        result =re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"', cmd_result.return_string)
        if not result:
            raise Exception("cannot get unit info!")
        for board_info in result:
                unittype_list.append("{0}-{1}-{2},{3}".format(board_info[0],board_info[1],board_info[2],unitlist.get(board_info[8])))
        return unittype_list
#获取实际要取内存的单板信息
    @staticmethod
    def get_collect_board(valid_board,board_module,board_unit):
        boardlist=[]


#获取前插有效模块单板类型
        for i in range(0,len(valid_board)):
            for j in range(0,len(board_module)):
                if valid_board[i]==board_module[j].split(',')[0]:
                    boardlist.append(board_module[j])
##                    break


#获取后插有效模块单板类型
        for i in range(0,len(valid_board)):
            for j in range(0,len(board_unit)):
                if valid_board[i]==board_unit[j].split(',')[0]:
                    boardlist.append(board_unit[j])
##                    break


        return boardlist


#获取执行获取反导命令文件
    @staticmethod
    def run_get_commandmml(umac_dut):
        result=-1
        try:
            cmd = 'EXPT MML:TYPE="PHY"&"SERV";'
            cmd_result = umac_dut.execute_command(cmd)
            context=cmd_result.return_string
##            logger.info(context)
            result=context.find('SYS_ERRMSG')


        except:
            result= -1
        return result

#循环获取前台单板状态，直到和升级前一致
    @staticmethod
    def get_boardstatus(umac_dut,board):
        boardlist=board
        alllist=[]
        validlist=[]
        count=0
        boardstatus=True
        while (boardlist!=validlist):
            alllist=umacBoardstatusinfo.get_board_info(umac_dut)
            validlist=umacBoardstatusinfo.get_valid_board(alllist)
            validlist.sort()
            logger.info('Now is check board status,before upgrade'+ str(boardlist)+'is normal')
            logger.info('Now is check board status,after upgrade'+ str(validlist)+'is normal')
            time.sleep(10)
            count=count+1
  #防止死循环，循环40次还是不一样，退出循环，相当于最长等15分钟
            if count==90:
                break
        return boardstatus

#获取协议栈配置数据
    @staticmethod
    def get_ipstackall(umac_dut):
        time.sleep(3)
        cmd = 'IPSTACK;'
        cmd_result = umac_dut.execute_command(cmd)
##        context=cmd_result.return_string
        time.sleep(1)
        cmd = 'SHOW IPSTACK ALL;'
        cmd_result = umac_dut.execute_command(cmd)
        result=cmd_result.return_string
        result=result.replace('",SYS_RESULT="0",SYS_LASTPACK="0";ACK SHOW IPSTACK ALL:INFO="!','')
        result=result.replace('",SYS_RESULT="0",SYS_LASTPACK="0";ACK SHOW IPSTACK ALL:INFO="','')
        time.sleep(5)
        cmd = 'EXIT MODE;'
##        logger.info(result)
        return result

###获取协议栈配置数据
##    @staticmethod
##    def get_ipstackall(umac_dut):











if __name__ == '__main__':
    file_list1 = ["aa.pkg", "a.pkg"]
    file_list2 = ["c:/cc/a.pkg", "c:/dd/c.pkg"]
##    print IndependentBoardManagement.check_file_list1_in_file_list_2(file_list1, file_list2)
