#coding=utf-8
'''
Created on 2014年11月21日

@author: 10077668
'''
import os
import inspect

class ChannelData(object):
    def __init__(self):
        self._channel_package_dict = {}

        for root, dirs, files in os.walk(self._get_current_path()):
            for file_name in files:   
                class_name = file_name.split(".")[0]
                if self._is_need_to_record(root, file_name, class_name):
                    root_list = root[root.rfind('infrastructure'):].split(os.sep)
                    root_list.insert(0, 'testlib')
                    self._channel_package_dict[class_name] = '.'.join(root_list)
                    
    def get_package(self, channel_type):
        return self._channel_package_dict[channel_type] + '.' + channel_type
    
    def _get_current_path(self):
        this_file = inspect.getfile(inspect.currentframe())
        return os.path.abspath(os.path.dirname(this_file))
    
    def _is_need_to_record(self, root, file_name, class_name):
        if self._is_python_file(file_name)\
                and not self._is_current_path(root) \
                and not self._is_init_file(class_name):
            return True
        return False
    
    def _is_current_path(self, path):
        if self._get_current_path() == path:
            return True
        return False
    
    def _is_python_file(self, name):
        if '.py' == os.path.splitext(name)[1]:
            return True
        return False
    
    def _is_init_file(self, name):
        if '__init__' == name:
            return True
        return False
    
if __name__ == '__main__':
    channel_data = ChannelData()
    print channel_data._channel_package_dict
    print channel_data.get_package('Telnet')
