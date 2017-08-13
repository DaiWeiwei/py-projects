# coding=utf-8
from Telnet import Telnet
import copy
import re


class XgwTelnet(Telnet):

    def excute_cmd(self, cmd_obj):
        #cmd_obj.timeout = 3.5
        if cmd_obj.command is not None:
            return self._excute_copyer(cmd_obj)
        if cmd_obj.expected is not None and cmd_obj.cmd_result.result:
            cmd_obj = Telnet.read(self, cmd_obj)
        return cmd_obj.cmd_result

    def _excute_copyer(self, cmd_obj):
        device_cmd_copyer = copy.deepcopy(cmd_obj)
        command_list = re.findall('^(.+)$', cmd_obj.command, re.M)
        for command in command_list:
            device_cmd_copyer.command = command
            cmd_result = Telnet.excute_cmd(self, device_cmd_copyer)
            if cmd_result.result:
                cmd_obj.cmd_result.return_string = cmd_obj.cmd_result.return_string + cmd_result.return_string
            else:
                return cmd_result
        return cmd_obj.cmd_result

    def is_connected(self):
        try:
            self._tn.write('\n')
        except:
            return False
        else:
            return True

if __name__ == '__main__':
    ret = '''
  no bearer-content 1
 bearer-content 1
operation-code 1
eps-bearer-id 6
qos qci 6 arp pvi 1 pl 1 pci 1 mbr 1000 1000 gbr 1000 1000
tft 3 ipv4 50.4.60.127 255.255.255.255 direction 3 Priority 1
exit
bearer-activate imsi 460017100650539 link-bearer 5 content1 1
show pgw bearer-content 1
'''
#     pattern = re.compile('^(.+)$', re.M)
#     match = pattern.search(ret)
    match = re.findall('^(.+)$', ret, re.M)
    print match


