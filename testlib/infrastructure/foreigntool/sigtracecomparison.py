#! usr/bin/python
# coding=utf-8
import os
import win32gui
import win32con
import struct
from ctypes import *
from robot.api import logger
import subprocess
import time
from testlib.infrastructure.utility.wmi import WMI
from testlib.infrastructure.foreigntool.copydatastruct import CopyDataStructure
from testlib.infrastructure.foreigntool.EventId import EVENT_ID_OF_SEND_TO_SIGNAL_TRACE_COMPARISON_TOOL


class SigalTraceComparison(object):
    def __init__(self, signal_trace_path_0, signal_trace_path_1, result_path, tool_path):
        self._signal_trace_path_0 = signal_trace_path_0
        self._signal_trace_path_1 = signal_trace_path_1
        self._result_path = result_path
        self._tool_path = tool_path
        _, self._tool_name = os.path.split(tool_path)
        self._tool_tile = "{0} - {1}".format(self._tool_name[0:-4], self._tool_name[0:-4])

    @property
    def old_path(self):
        return self._signal_trace_path_0

    @property
    def new_path(self):
        return self._signal_trace_path_1

    @property
    def result_file(self):
        return "{0}/result.csv".format(self._result_path)

    def _find_ompare_tool(self):
        wmi = WMI()
        for p in wmi.Win32_Process(name=self._tool_name):
            return True
        return False

    @staticmethod
    def _open_exe(exe_file, sleep_time=0):
        subprocess.Popen(exe_file)
        time.sleep(sleep_time)

    def _check_path(self):
        if not os.path.exists(self.old_path):
            raise Exception("{0} not exists".format(self.old_path))
        if not os.path.exists(self.new_path):
            raise Exception("{0} not exists".format(self.new_path))
        if not os.path.exists(self._tool_path):
            raise Exception("{0} not exists".format(self._tool_path))

    def compare(self):
        self._check_path()
        if not self._find_ompare_tool():
            self._open_exe(self._tool_path, 5)
        tool_hwnd = win32gui.FindWindow(None, self._tool_tile)
        if not tool_hwnd:
            logger.warn('cannot open [{0}]'.format(self._tool_path))
            return False

        # result = tagPsttCopyData()

        old_path = self.old_path
        new_path = self.new_path

        struct_string = struct.pack("255s255s255sLL", old_path, new_path, self.result_file, 0, 0)

        send_to_tool = CopyDataStructure()
        send_to_tool.dwData = EVENT_ID_OF_SEND_TO_SIGNAL_TRACE_COMPARISON_TOOL
        send_to_tool.cbData = len(struct_string)

        string_struct = create_string_buffer(struct_string, 1000)
        address_of_string_struct = addressof(string_struct)
        cast(address_of_string_struct, POINTER(c_void_p))
        send_to_tool.lpData = address_of_string_struct

        logger.info("result file:{0}".format(self.result_file))

        result = win32gui.SendMessage(tool_hwnd, win32con.WM_COPYDATA, None, addressof(send_to_tool))
        # minimize window
        win32gui.SendMessage(tool_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)

        return result


if __name__ == '__main__':
    comparison = SigalTraceComparison(r'F:\signal_trace_data',
                                      r'E:\linxing\OMCCMDTool-linxing\1OMCCMDTool-linxing\release')
    print comparison.compare()
