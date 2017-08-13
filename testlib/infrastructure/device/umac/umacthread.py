# coding=utf-8
import threading
import time
from testlib.infrastructure.utility import ThreadLogger
from testlib.infrastructure.device.umac.umac import uMac


class UmacThread(object):
    def __init__(self, host, port, user_name, password, office_id, flag):
        self._umac = uMac(host, port, user_name, password, office_id, flag)
        self._cmd_result_list = []
        self._run_finish = True
        self._timeout = 10
        self._flag = flag

    @property
    def flag(self):
        return self._flag

    def execute_command(self, cmd_list, timeout=45 * 60):
        if type(cmd_list) is not list:
            cmd_list = [cmd_list]
        self._cmd_list = cmd_list
        self._timeout = timeout
        self._start_send_cmd_thread()
        # self._execute_cmd()

    def _start_send_cmd_thread(self):
        self.__send_cmd_thread = threading.Thread(
            target=self._execute_cmd_list)
        self.__send_cmd_thread.daemon = True
        self.__send_cmd_thread.start()
        time.sleep(0.1)

    def _execute_cmd_list(self):
        self._run_finish = False
        self._umac.logout()
        #self._umac.login()
        for _cmd in self._cmd_list:
            try:
                # ThreadLogger.cache_log("cmd:%s" % _cmd, "INFO")
                print 'cmd:',_cmd
                cmd_result = self._umac.execute_command(_cmd, self._timeout)
                self._cmd_result_list.append(cmd_result)
                time.sleep(5)
                # ThreadLogger.cache_log("cmd finish:%s" % _cmd, "INFO")
            except Exception, e1:
                raise Exception("load ind board version fail:cmd = {0},reason = {1}".format(_cmd, e1))
        self._run_finish = True

    def is_run_finish(self):
        return self._run_finish

    @property
    def cmd_result_list(self):
        return self._cmd_result_list

    def close(self):
        try:
            self._umac.logout()
            self.__send_cmd_thread.join()
        except:
            pass
        self._run_finish = True

    def __del__(self):
        try:
            self.close()
        except:
            pass


if __name__ == '__main__':
    umacList = []
    for i in range(5):
        umac = UmacThread('30.1.136.232', '7722', 'admin', '', '51', str(i))
        umacList.append(umac)
    # umac.login()
    cmd_list = ['ADD INDPKG:ID=201,PKGNAME="EGBS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg";',
                'ADD INDPKG:ID=202,PKGNAME="EGFS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg";',
                'ADD INDPKG:ID=204,PKGNAME="EGBS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg";',
                'ADD INDPKG:ID=205,PKGNAME="EGFS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg";',
                'ADD INDPKG:ID=207,PKGNAME="EGBS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg";',
                'ADD INDPKG:ID=208,PKGNAME="EGFS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg";']
    for idx,umac in enumerate(umacList):
        print 'cmd:',cmd_list[idx]
        umac.execute_command(cmd_list[idx])

    for umac in umacList:
        print umac._umac._channel

    import time
    time.sleep(30*60)
##    cmd = ['SHOW INDBOARD;', 'SHOW INDRUNSW:ID=129,ADDR=1-2-29-1;']
##
##    t1 = time.time()
##    umac.execute_command(cmd, 5)
##    while not umac.is_run_finish():
##        print 'running:', time.time() - t1
##        time.sleep(1)
##    for cmd_result in umac.cmd_result_list:
##        print cmd_result.return_string
##    umac.close()
