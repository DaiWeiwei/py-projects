#coding=utf-8
'''
Created on 2014�?0�?2�?

@author: wangjianxiong
'''
from DeviceRepository import DeviceRepository
from DeviceReflection import DeviceReflection
from testlib.infrastructure.device.UsecaseInfoRecorder import UsecaseInfoRecorder

class DeviceFactory(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        
    @staticmethod               
    def create(device_type, device_key, *args):
        UsecaseInfoRecorder.record_rf_time()
        device_obj = DeviceRepository().find(device_key)
        if None == device_obj:
            device_obj = DeviceReflection().create_obj(device_type, *args)
            DeviceRepository().add(device_key, device_obj)
        return device_obj 

if __name__ == '__main__':
    hoc = DeviceFactory.create('Hoc', 'Hoc:145','10.9.144.145', 23)
    cmd_result = hoc.set_port_value('1,2','30,30')
    print cmd_result.return_info
#     mcpc.login()
#     print mcpc.base_info(1).return_string
#     print mcpc.ps_release(1).return_string
#     print mcpc.ps_call(1).return_string
#     print mcpc.ps_release(1).return_string
#     mcpc.loginout()

    