#coding=utf-8
'''
Created on 2014年11月6日

@author: 10077668
'''
from testlib.infrastructure.device.CmdResult import CmdResult

class DeviceCmd():
    '''
    classdocs
    '''
    def __init__(self, command, expected = None, timeout = 5):
        self._command = command
        self._expected = expected
        self._timeout = timeout
        self._cmd_result = CmdResult()
        
    def fail_to_excute(self, fail_reason):
        self._cmd_result.fail_to_excute(fail_reason)
        
    def success_to_excute(self, return_string):
        self._cmd_result.success_to_excute(return_string)
    
    @property  
    def command(self):  
        return self._command  

    @property  
    def expected(self):  
        return self._expected  
    
    @property  
    def timeout(self):  
        return self._timeout 
    
    @property  
    def cmd_result(self):  
        return self._cmd_result  
    
        
    