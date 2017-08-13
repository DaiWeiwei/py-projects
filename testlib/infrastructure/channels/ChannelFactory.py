#coding=utf-8
'''
Created on 2014�?0�?0�?

@author: wangjianxiong
'''

from time import sleep
from testlib.infrastructure.utility.Reflection import Reflection
from testlib.infrastructure.utility.Singleton import Singleton
#from testlib.infrastructure.utility.LteLog import *
from testlib.infrastructure.channels.ChannelData import ChannelData

@Singleton
class ChannelFactory(object):
    '''
    通道的工厂类
    '''

    def __init__(self):
        '''
        Constructor
        '''
#         log_config()
        self._channels = {}
        self._channel_data = ChannelData()

    def _find_channel(self, uniId):
        if uniId in self._channels :
            return self._channels[uniId]
        else :
            return None

    def _delete_channel(self, uniId):
        if self._find_channel(uniId) is not None :
            self._channels.pop(uniId)

    def _add_channel(self, uniId, ob):
            self._channels[uniId] = ob

    #工厂类对外暴露的接口                
    def create(self, channel_type, host, port,flag = "0", timeout = 5, mode = None):
        reflection = Reflection()
        tn = reflection.create_obj(self._channel_data.get_package(channel_type), \
                                   channel_type, host, port,flag, timeout)
        uniId = tn.get_id()
        ob = self._find_channel(uniId)
        if ob is None :
            tn.connect()
            ob = tn
        else:
            ob.disconnect()
            sleep(1)
            ob.connect()
        self._add_channel(uniId, ob)
        return ob

    def get_channels(self):
        return self._channels

    def close_channels(self):
        for i in self._channels :
            self._channels[i].disconnect()
        self._channels.clear()
#
# if __name__ == '__main__':
#     fac = ChannelFactory()
#     fac2 = ChannelFactory()
#     while(1):
#         tn = fac.create('Telnet','10.92.232.180','64116')
#         tn.read('username:', 10)
#         print tn.excute_cmd('admin', 'password:', 10)
#         print tn.excute_cmd('', '$>', 10)
#         tn2 = fac2.create('Telnet','10.92.232.180','64116')
#         tn2.read('username:', 10)
#         print tn2.excute_cmd('admin', 'password:', 10)
#         print tn2.excute_cmd('', '$>', 10)
#         tn.excute_cmd('sdfsdf', '$>', 10)
#         tn3 = fac.create('Telnet','10.92.232.180','64116')
#         tn3.read('username:', 10)
#         print tn3.excute_cmd('admin', 'password:', 10)
#         print tn3.excute_cmd('', '$>', 10)
#         tn.excute_cmd('sdfsdfsdf', '$>', 10)
#         tn2.excute_cmd('sdfsdfsdf', '$>', 10)
#         tn3.excute_cmd('sdfsdfsdf', '$>', 10)
#      
    
    
            
        