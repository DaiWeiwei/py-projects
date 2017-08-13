# coding=utf-8
'''
Created on 2014�?0�?2�?

@author: Administrator
'''
from robot.api import logger
import inspect
import time
from testlib.infrastructure.utility.Reflection import Reflection
from testlib.infrastructure.device.DeviceCmd import DeviceCmd


class Device(object):
    '''
    classdocs
    '''
    def __init__(self, *args):
        '''
        Constructor
        '''
        self._expected = None
        self._timeout = None
        self._channel = None

    def login(self):
        pass

    def _func_name(self):
        return inspect.stack()[1][3]

    def _assemble_cmd(self, func_name, *args):
        return Reflection().invoke(self._cmd, func_name, *args)

    def excute_channel_cmd_safe(self, cmd, expected, timeout=5):
        cmd_result = self.excute_channel_cmd(cmd, expected, timeout)
        if not cmd_result.result:
            self.login()
            cmd_result = self.excute_channel_cmd(cmd, expected, timeout)
        return cmd_result

    def excute_channel_cmd(self, cmd, expected, timeout=5):
        # if len(cmd) > 0 and cmd[-1] != ';':
        #     cmd += ';'
        return self._channel.excute_cmd(DeviceCmd(cmd, expected, timeout))

    def excute_channel_write(self, cmd):
        return self.excute_channel_cmd(cmd, None)

    def excute_channel_read(self, expected='', timeout=5):
        return self.excute_channel_cmd(None, expected, timeout)

    def _excute_parse(self, func_name, device_cmd):
        cmd_result = Reflection().invoke(self._parser, func_name, device_cmd)
        if not cmd_result.result:
            logger.debug(cmd_result.return_string)
        return cmd_result

    def _excute_compound_cmd(self, func_name, expected, timeout, *args):
        cmd = self._assemble_cmd(func_name, *args)
        logger.info("device send : {0}".format(cmd))
        cmd_result = self.excute_channel_cmd_safe(cmd, expected, timeout)
        logger.info("device recv : {0}".format(cmd_result.return_string))
        cmd_result = self._excute_parse(func_name, cmd_result)
        return cmd_result

    def _excute_compound_cmd_repeat(self, func_name, expected, timeout, *args, **kwargs):
        repeat_times, wait_time = self._get_kwargs_value(kwargs)
        while repeat_times + 1:
            cmd_result = self._excute_compound_cmd(func_name, expected, timeout, *args)
            if cmd_result.result:
                break
            repeat_times = repeat_times - 1
            time.sleep(wait_time)
        return cmd_result

    def _excute_compound_cmd_no_response(self, func_name, *args):
        cmd = self._assemble_cmd(func_name, *args)
        logger.debug("device send : {0}".format(cmd))
        return self.excute_channel_write(cmd)

    def _get_kwargs_value(self, params_dict):
        repeat_times = 3
        wait_time = 3
        if params_dict.has_key('repeat'):
            repeat_times = params_dict['repeat']
        if params_dict.has_key('wait_time'):
            wait_time = params_dict['wait_time']
        return repeat_times, wait_time

