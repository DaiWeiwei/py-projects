# coding:utf-8
import os
import time
import subprocess
import win32gui
import win32con
import struct
from ctypes import *
from robot.output import LOGGER
from testlib.infrastructure.foreigntool.copydatastruct import CopyDataStructure
from testlib.infrastructure.foreigntool.EventId import EVENT_ID_OF_SEND_TO_SHOW_RUNNING_CMD_SORT_TOOL
from testlib.infrastructure.utility.wmi import WMI


class ShowRunningCommandSort(object):
    def __init__(self, show_running_file):
        self._show_running_file = show_running_file
        self._show_running_sort_file = self._show_running_file.replace('.txt', '_sort.txt')
        self._tool_path = os.path.join(__file__, '../../../../../tool/show_running_cmd_sort/ShowRunningCmdSort.exe')
        #self._tool_path = r'E:\linxing\cmd_sort\Debug\ShowRunningCmdSort.exe'
        LOGGER.info('show running command sort tool:' + self._tool_path)
        _, self._tool_name = os.path.split(self._tool_path)
        self._tool_tile = "{0}".format(self._tool_name[0:-4])
        self._process = None

    @property
    def show_running_sort_file(self):
        return self._show_running_sort_file

    def _find_tool(self):
        wmi = WMI()
        for p in wmi.Win32_Process(name=self._tool_name):
            return True
        return False

    def _open_exe(self, exe_file, sleep_time=0):
        self._process = subprocess.Popen(exe_file)
        time.sleep(sleep_time)

    def _check_path(self):
        if not os.path.exists(self._show_running_file):
            LOGGER.error("ShowRunningCommandSort:{0} not exists".format(self._show_running_file))
            return False
        return True

    def sort_cmd(self):
        if not self._check_path():
            return False
        if not self._find_tool():
            self._open_exe(self._tool_path, 5)
        tool_hwnd = win32gui.FindWindow(None, self._tool_tile)
        if not tool_hwnd:
            LOGGER.error('cannot open [{0}]'.format(self._tool_path))
            return False

        struct_string = struct.pack("255s255s", self._show_running_file,
                                    self._show_running_sort_file)

        send_to_tool = CopyDataStructure()
        send_to_tool.dwData = EVENT_ID_OF_SEND_TO_SHOW_RUNNING_CMD_SORT_TOOL
        send_to_tool.cbData = len(struct_string)

        string_struct = create_string_buffer(struct_string, 1000)
        address_of_string_struct = addressof(string_struct)
        cast(address_of_string_struct, POINTER(c_void_p))
        send_to_tool.lpData = address_of_string_struct

        LOGGER.info("show running:{0}".format(self._show_running_file))
        LOGGER.info("show running cmd sort :{0}".format(self._show_running_sort_file))

        result = win32gui.SendMessage(tool_hwnd, win32con.WM_COPYDATA, None, addressof(send_to_tool))
        win32gui.SendMessage(tool_hwnd, win32con.WM_CLOSE)
        return result

    def release(self):
        if not self._process:
            return
        if self._process.stdin:
            self._process.stdin.close()
        if self._process.stdout:
            self._process.stdout.close()
        if self._process.stderr:
            self._process.stderr.close()
        try:
            self._process.kill()
        except OSError:
            pass


if __name__ == '__main__':
    sr = ShowRunningCommandSort(r'E:\linxing\iTest\branches\code\iTest\RIDE-1.4_1119\robot\temp\show_running.txt')
    print sr.sort_cmd()
