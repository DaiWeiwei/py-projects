# coding=utf-8
import logging
import re

from testlib.infrastructure.device.Device import Device
from testlib.infrastructure.device.DeviceCmd import DeviceCmd
from testlib.infrastructure.channels.ChannelFactory import ChannelFactory
from testlib.infrastructure.device.CmdResult import CmdResult

class Xgw(Device):
    def __init__(self, host, xgw_port='23',user_name = 'zte',password = 'zte', version=None):
        self._version = "xgw 1.0"#XgwVersion(version)
        self._timeout = 10
        self._expected = 'success|fail|timeout'
        self._host = host
        self._xgw_port = xgw_port
        self._username = user_name
        self._password = password
        self.prompt = "#"
        self._name = "XgwTelnet"
        self._channel = None
        #self.cmd_result = self.login()  # todo 需要的时候才login

    def login(self):
        if self.is_connected():
            return CmdResult()
        if self._host is None:  # todo 单元测试不通过，临时增加，后续改为需要时才login后删除，
            return CmdResult()

        self._channel = ChannelFactory().create(self._name,
                                                    self._host,
                                                    self._xgw_port)
        self._channel.pagebreak = '--More--'
        self.excute_channel_read('Username:')
        self._channel.excute_cmd(DeviceCmd(self._username, 'Password'))
        cmd_result = self._channel.excute_cmd(DeviceCmd(self._password, '#'))
        if re.search('incomplete|error', cmd_result.return_string):
            logging.error('xgw login fail, please check user/pw')
            cmd_result.result = False
        return cmd_result

    def logout(self):
        if self._channel is not None:
            self._channel.disconnect()

        cmd_result = CmdResult()
        cmd_result.success_to_excute('succ to logout')
        return cmd_result

    def is_connected(self):
        if not self._channel:
            return False
        return self._channel.is_connected()

    def execute_command(self, xgw_para_list):
        self.prepare_for_execute_command()
        return self._excute_compound_cmd(self._func_name(),
                                         self._expected,
                                         self._timeout,
                                         xgw_para_list)

    def prepare_for_execute_command(self):
        cmd_result = self.login()
        if not cmd_result.result:
            raise Exception("fail to connect to Telnet")


if __name__ == '__main__':
    xgw = Xgw('10.42.188.56')
    cmd = 'show synchronization'
    xgw.login()

    # cmd = 'show pgw cpu-dpi-info'
    # cmd_result = xgw.excute_channel_cmd(cmd, '#', 5)
    # pattern = '(DPI_\w+)|(\w+.bin)'
    # result = re.findall(pattern,cmd_result.return_string)
    # dpi_files = []
    # for i in range(0,len(result))[::2]:
    #     dpi_files.append('{0}{1}'.format(result[i][0],result[i+1][1]))
    # print dpi_files

    cmd = 'show ip interface brief'
    cmd_result = xgw.excute_channel_cmd(cmd, '#', 5)
    pattern = '(gei-[\d/]+)\s+[^\s]+\s+[^\s]+\s+(\w+)\s+(\w+)\s+(\w+)'
    result = re.findall(pattern,cmd_result.return_string)
    print result

    dict_port_status = {}
    for port_status in result:
        dict_port_status[port_status[0]] = [port_status[1], port_status[2], port_status[3]]
    print dict_port_status
    # aa = cmd_result.return_string[cmd_result.return_string.find('Location'):]
    # print aa
    # if aa.find('Slave'):
    #     print u'先拔出备板后，再升级'
    # else:
    #     print u'升级'
    xgw.logout()
    # for cmd in cmd_list:
    #     xgw.excute_channel_cmd(cmd, '#', 5)
    # cmd_show = 'show xgw info'
    # xgw.excute_channel_cmd(cmd_show, 'Netelement type:\s*1XDPI', 5)
