#coding=utf-8
'''
Created on 2014年11月7日

@author: 10077668
'''

class CmdResult():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._result = True
        self._fail_reason = ''
        self._return_info = {}
        self._return_string = ''
    
    def fail_to_excute(self, fail_reason):
        self._result = False
        self._fail_reason = fail_reason
        
    def success_to_excute(self, return_string):
        self._result = True
        self._return_string = return_string
        
    def success_to_parse(self, return_info):
        self._result = True
        self._return_info = return_info
    
    @property  
    def result(self):  
        return self._result 
    
    @property  
    def fail_reason(self):  
        return self._fail_reason  

    @property  
    def return_info(self):  
        return self._return_info  
    
    @property  
    def return_string(self):  
        return self._return_string  
    