#coding:utf-8
import time

class NeGeneration:
    def __init__(self,umac_dut):
        self._umac_dut = umac_dut
        self._umac_dut.login_clean()
        self._rnc = self._has_rnc()#false:no 2g
        self._nse = self._has_nse()#false:no 3g
        self._ta = self._has_ta()#false:no 4g
        umac_dut.logout()

    def get_result(self):
        return self._rnc, self._nse,self._ta

    def _has_rnc(self):
        return self._run_cmd('show rnc;')

    def _has_nse(self):
        return self._run_cmd('show nse;')

    def _has_ta(self):
        return self._run_cmd('show ta;')

    def _run_cmd(self,cmd):
        try:
            cmd_result = self._umac_dut.execute_command(cmd)
            return "info=" in cmd_result.return_string.lower()
        except:
            return False