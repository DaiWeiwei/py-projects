# coding=utf-8
import logging
import re
import time
from testlib.infrastructure.device.Device import Device
from testlib.infrastructure.device.DeviceCmd import DeviceCmd
from testlib.infrastructure.channels.ChannelFactory import ChannelFactory
from testlib.infrastructure.device.CmdResult import CmdResult


class uMac(Device):
    def __init__(self, host, port='7722', user_name='zte', password='zte', office_id=None,flag = "0", version=None):
        self._version = "umac 1.0"  # XgwVersion(version)
        self._timeout = 10
        self._expected = 'success|fail|timeout'
        self._host = host
        self._port = port
        self._username = user_name
        self._password = password
        self._office_id = office_id
        self.prompt = "$"
        self._channel = None
        self._name = "uMacTelnet"
        self._common_expect = 'SYS.LASTPACK=.?1.?'  # 'SYS_RESULT=\"{0,1}\d+\"{0,1}'
        self._flag = flag
        #self.cmd_result = self.login()  # todo 需要的时候才login

    def login(self):
        if self.is_connected():
             return CmdResult()
        # if self._host is None:  # todo 单元测试不通过，临时增加，后续改为需要时才login后删除，
        #     return CmdResult()
        self._channel = ChannelFactory().create(self._name,
                                                    self._host,
                                                    self._port,
                                                    self._flag)
        self._channel.pagebreak = '--More--'
        cmd_result = self._channel.excute_cmd(
            DeviceCmd("set ndfne:id={0};".format(self._office_id), self._common_expect))

        if 'ID={0}'.format(self._office_id) not in cmd_result.return_string:
            logging.info(cmd_result.return_string)
            self.logout()
            return False
        cmd_result = self._channel.excute_cmd(
            DeviceCmd("SLOGIN:NAME={0},pwd={1};".format(self._username, self._password), self._common_expect))
        if 'ACK SLOGIN:SYS_RESULT="0"' not in cmd_result.return_string:
            logging.info(cmd_result.return_string)
            self.logout()
            return False
        # self.excute_channel_read('Username:')
        # self._channel.excute_cmd(DeviceCmd(self._username, 'Password'))
        # cmd_result = self._channel.excute_cmd(DeviceCmd(self._password, '#'))
        # if re.search('incomplete|error', cmd_result.return_string):
        #     logging.error('xgw login fail, please check user/pw')
        #     cmd_result.result = False
        # return cmd_result
        return True

    def logout(self):
        if self._channel is not None:
            self._channel.disconnect()
        self._channel = None
        cmd_result = CmdResult()
        cmd_result.success_to_excute('succ to logout')
        return cmd_result

    def is_connected(self):
        #if not self._channel:
        #    return False
        try:
            return self._channel.is_connected()
        except:
            return False

    def _login2(self):
        try:
            return self.login()
        except:
            return False
    def login_with_try(self,try_times):
        temp_try_times = try_times
        while temp_try_times:
            if self._login2():
                logging.info('umac try loggin succ, try time = {0}'.format(try_times - temp_try_times))
                return True
            logging.warn('umac try loggin fail, try time = {0}'.format(try_times - temp_try_times))
            temp_try_times -= 1
            time.sleep(5)
        return False

    def login_clean(self,try_times = 20):
        logging.info('login clean...')
        logging.info('logout...')
        self.logout()
        time.sleep(2)
        logging.info('login_with_try,times={0}'.format(try_times))
        return self.login_with_try(try_times)
    def check_connected(self, timeout, per_time_sleep):
        if timeout < per_time_sleep:
            timeout - per_time_sleep
        time_start = time.time()
        while (time.time() - time_start) <= timeout:
            if self._login2():
                return True
            time.sleep(per_time_sleep)
        return False

    def execute_command(self, cmd, timeout = 120,try_times = 1,try_sleep=0):
        self.prepare_for_execute_command()
        if type(cmd) is not str:
            raise Exception("umac execute_command :cmd only support str")
        #logging.debug("cmd:{0}".format(cmd))
        while try_times:
            cmd_result = self.excute_channel_cmd(cmd,self._common_expect,timeout)
            if cmd_result and cmd_result.return_string.find('SYS_ERRMSG')>=0:
                logging.info("find sys_errormsg, try again, left {0}...".format(try_times-1))
                try_times -= 1
                time.sleep(try_sleep)
            else:
                break

        #logging.debug("cmd result:{0}".format(cmd_result.return_string))
        return cmd_result

        # return self._excute_compound_cmd(self._func_name(),
        #                                  self._expected,
        #                                  self._timeout,
        #                                  xgw_para_list)

    def prepare_for_execute_command(self):
        if not self.login():
            raise Exception("fail to connect to Telnet")


if __name__ == '__main__':
    import re
    #umac = uMac('192.0.19.10', '7722', 'admin', '', '20','119')
    #umac = uMac('30.1.136.163', '7722', 'admin', '', '107', "1")
    umac = uMac('30.1.136.167', '7722', 'admin', '', '253', "1")
    umac.login()

    #cmd = 'EXPT MML:TYPE="SERV";'
    #cmd = 'SHOW INDRUNSW:ID=119,ADDR=1-2-19-1;'
    #cmd = 'SHOW INDBOARD;'
    #cmd = 'SHOW MODULE:MTYPE="UOMP";'
    #cmd = 'SHOW CPUSTATE:RACK=1,SHELF=2,SLOT=7,CPUNO=1,LCPUNO=1;'
    cmd = 'show rnc;'
    cmd_result = umac.execute_command(cmd)
    print cmd_result.return_string
    #cmd_result = '''ACK SHOW INDRUNSW:SYS_RESULT="0",SYS_LASTPACK="0";ACK SHOW INDRUNSW:INFO="EGFS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg"-"1.10.00.P16.B10a"-"285884426"&"EGFS-83XX-X200A5-REL_2_6_80.ubf"-"02.06.00.80"-"33947728",SYS_RESULT="0",SYS_LASTPACK="1"&="EGFS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg"-"1.10.00.P16.B10a"-"285884426"&="EGFS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg"-"1.10.00.P16.B10a"-"285884426"'''

    #pattern = '"([^"]+\.pkg)"'

    #print re.findall(pattern,cmd_result)
    # pattern = '[=&]"(\d+)"-"(\d+)"-"\d+"-"\d+"-"(\d+)"'
    # result = re.findall(pattern, cmd_result.return_string)
    # print result
    # r = re.findall('[=&]"(\d+)"-"(\d+)"',cmd_result.return_string)
    # print r
    # cmd = 'DEL USELESS INDPKG:ID=119;'
    # cmd_result = umac.excute_channel_cmd(cmd, umac._common_expect, 30)
    #print cmd_result.return_string

    #print cmd_result.return_string
    #print umac.check_connected(15 * 60, 30)
    #print umac.is_connected()
    # print umac.cmd_result

    # cmd_show = 'SHOW CMD:LEVEL="SM_SYSTEMLEVEL_4";'
    # # cmd_list = ['end', 'con t', 'xgw', 'pgw']
    # # for cmd in cmd_list:
    # #     xgw.excute_channel_cmd(cmd, '#', 5)
    # # cmd_show = 'show xgw info'
    # cmd_result = umac.excute_channel_cmd(cmd_show, umac._common_expect, 20)
    # print cmd_result.return_string
    #
    # show_commands = []
    # for line in cmd_result.return_string.split('&'):
    #     show_commands.append(line.split('"-"')[1].strip('"'))
    #
    # with open("c:/commands.txt",'w+') as f :
    #     f.write("\n".join(show_commands))

    # result = []
    # import time
    # for cmd in show_commands:
    #     time.sleep(0.1)
    #     cmd_result = umac.excute_channel_cmd(cmd, umac._common_expect, 5)
    #     result.append(cmd_result.return_string)
    #
    # with open("c:/aa1.txt",'w+') as f :
    #     f.write("\r\n".join(result))
