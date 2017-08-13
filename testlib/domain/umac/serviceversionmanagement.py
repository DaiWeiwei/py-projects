# coding=utf-8
import re
import os
import time
from robot.api import logger


class ServiceVersionManagement(object):
    @staticmethod
    def delete_useless_version_files(umac_dut):
        try:
            cmd = 'DEL USELESSPKG;'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd)
        except:
            pass

    @staticmethod
    def backup_zdb(umac_dut):
        try:
            cmd = 'UPG ONETIME:MODE="BACKUP";'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 2 * 60)
        except:
            pass
    @staticmethod
    def backup_config_data(umac_dut):
        try:
            cmd = 'UPG ONETIME:MODE="BACKUP";'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 2 * 60)
        except:
            pass

    @staticmethod
    def backup_configdata_mml(umac_dut):
        try:
            cmd = ' BACKUP:OUTPUTPATH="/autobackup",FILENAME="allcfg",SETID=2&1025&1026&1027&1400000&1400001;'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 2 * 60)
        except:
            pass

    @staticmethod
    def backup_current_alarm_mml(umac_dut):
        try:
            cmd = ' SHOW FAULTALARM'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 2 * 60)
        except:
            pass


    @staticmethod
    def upgrade_zdb(umac_dut):
        try:
            cmd = 'UPG ONETIME:MODE="UPGRADE";'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 2 * 60)
        except:
            logger.warn("fail: run cmd = {0},timeout = 120s".format(cmd))
            pass

    @staticmethod
    def load_and_active_version(umac_dut):
        try:
            cmd = 'LOAD PKG:TYPE="LOAD"&"ACTIVE";'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 2 * 60)
        except:
            logger.warn("fail: run cmd = {0},timeout = 120s".format(cmd))
            pass

    @staticmethod
    def validate_version(umac_dut):
        ServiceVersionManagement._send_validate_cmd(umac_dut)
        time.sleep(60)
##        ServiceVersionManagement._check_restart_success(umac_dut)

    @staticmethod
    def _send_validate_cmd(umac_dut):
        try:
            cmd = 'ENABLE PKG;'
            logger.info("cmd:{0}".format(cmd))
            cmd_result = umac_dut.execute_command(cmd, 60)
        except:
            pass

    @staticmethod
    def _check_restart_success(umac_dut):
        module_info = ServiceVersionManagement._get_modle_info(umac_dut)
        while True:
            # left slot
            if (ServiceVersionManagement._show_cpu_status(umac_dut,
                                                          module_info[0],
                                                          module_info[1],
                                                          module_info[2],
                                                          module_info[4],
                                                          module_info[5])):
                break
            # right slot
            if (ServiceVersionManagement._show_cpu_status(umac_dut,
                                                          module_info[0],
                                                          module_info[1],
                                                          module_info[3],
                                                          module_info[3],
                                                          module_info[5])):
                break

            time.sleep(60)

    @staticmethod
    def _get_modle_info(umac_dut):
        cmd = 'SHOW MODULE:MTYPE="UOMP";'
        cmd_result = umac_dut.execute_command(cmd, 30)
        # Rack	Shelf	Left Slot	Right Slot	CPU	Logic CPU
        pattern = '="(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-'
        result = re.findall(pattern, cmd_result.return_string)
        if not result:
            raise Exception("get module fail:cmd={0},return={1}".format(cmd, cmd_result.return_string))
        return result[0]

    @staticmethod
    def _show_cpu_status(umac_dut, rack, shelf, slot, cpu_no, lcpu_no):
        try:
            cmd = 'SHOW CPUSTATE:RACK={0},SHELF={1},SLOT={2},CPUNO={3},LCPUNO={4};'.format(rack,
                                                                                           shelf,
                                                                                           slot,
                                                                                           cpu_no,
                                                                                           lcpu_no)
            cmd_result = umac_dut.execute_command(cmd, 5)
            result = re.findall('"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"-"1"', cmd_result.return_string)
            return not not result
        except:
            return False

    @staticmethod
    def syna(umac_dut):
        try:
            cmd = 'SYNA:STYPE="ALL";'
            umac_dut.execute_command(cmd, 300)
        except:
            logger.warn("fail: run cmd = {0},timeout = 300s".format(cmd))


if __name__ == '__main__':
    import re
    from testlib.infrastructure.device.umac.umac import uMac

    umac_dut = uMac('195.137.81.55', '7722', 'admin', '', '28', '119')
    ServiceVersionManagement._check_restart_success(umac_dut)
