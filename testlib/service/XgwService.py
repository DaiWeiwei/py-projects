import os
import re
import time
from robot.api import logger
from testlib.domain.xgw.xgwconfig import XgwConfig
from testlib.domain.ne.ConfigRepository import ConfigRepository
from testlib.infrastructure.device.xgw.Xgw import Xgw
from testlib.domain.TelnetRepository import TelnetRepository
from testlib.domain.xgw.xgwmanagement import XgwManagement
from testlib.domain.xgw.xgwsoftpara import XgwSoftPara
from testlib.domain.xgw.xgwshowrunning import XgwShowRunning
class XgwService(object):
    @staticmethod
    def init_xgw(xgw_name, **_xgw_config):
        xgw_config = _xgw_config['**_xgw_config']
        xgw_config_obj = XgwService.create_xgw_config(xgw_name, xgw_config)
        xgw_config_obj.print_config()

        XgwService.create_xgw_dut(xgw_name,
                                  xgw_config_obj.host,
                                  23,
                                  xgw_config_obj.telnet_user_name,
                                  xgw_config_obj.telnet_password
                                  )

    @staticmethod
    def set_ftp_and_load_mode(xgw_name):
        logger.info("set ftp and load mode")
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        xgw_dut.login()
        cmd_list = ['con t',
                    'ftp-server enable',
                    'ftp-server top-directory /sysdisk0/',
                    'load-mode txt',
                    'end']
        for cmd in cmd_list:
            xgw_dut.excute_channel_cmd(cmd, '#', 10)
        cmd_result = xgw_dut.excute_channel_cmd('write', '#', 120)
        xgw_dut.logout()

    @staticmethod
    def backup_xgw_zdb(xgw_name):
        xgw_config = XgwService.find_xgw_config(xgw_name)
        t = time.time()
        logger.info('start backup zdb...')
        XgwManagement.backup_zdb(xgw_config)
        logger.info('end backup zdb, {0}s'.format(time.time() - t))

    @staticmethod
    def check_mpu(xgw_name):
        logger.info('check mpu')
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        XgwManagement.check_mpu(xgw_dut)

    @staticmethod
    def set_version_start_style(xgw_name):
        logger.info('set version start style')
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        XgwManagement.set_version_start_style(xgw_dut)

    @staticmethod
    def upload_new_zdb(xgw_name):
        t = time.time()
        logger.info('start upload new zdb...')
        xgw_config = XgwService.find_xgw_config(xgw_name)
        XgwManagement.upload_new_zdb(xgw_config, xgw_config.new_version_in_local, '/sysdisk0/xgwconfig/DATA0')
        XgwManagement.upload_new_zdb(xgw_config, xgw_config.new_version_in_local, '/sysdisk0/xgwconfig/DATA1')
        logger.info('end upload new zdb, {0}s'.format(time.time() - t))

    @staticmethod
    def load_new_version(xgw_name):
        xgw_config = XgwService.find_xgw_config(xgw_name)
        xgw_config.set_upgrade()
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        XgwManagement.load_new_version(xgw_dut, xgw_config)

    @staticmethod
    def restart_fore_version(xgw_name, sleep_after_restart=2 * 60):
        t = time.time()
        logger.info('restart fore version...')
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        XgwManagement.restart_fore_version(xgw_dut)
        time.sleep(sleep_after_restart)
        logger.info('  try connect to fore version...')
        while True:
            try:
                xgw_dut.login()
                xgw_dut.excute_channel_cmd('end', '#', 2)
                break
            except:
                time.sleep(60)
        logger.info('connected to fore version, {0}s'.format(time.time() - t))

    @staticmethod
    def check_pgw_cpu_restart(xgw_name, before_show_group):
        logger.info('check pgw cpu restart...')
        t = time.time()
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        xgw_config = XgwService.find_xgw_config(xgw_name)

        XgwManagement.check_pgw_cpu_restart(xgw_dut, before_show_group, xgw_config.pgw_cpu_restart_max_time)
        logger.info('end check pgw cpu restart success, {0}s'.format(time.time() - t))

    @staticmethod
    def show_pgw_group(xgw_name):
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        return XgwManagement.show_pgw_group(xgw_dut)

    @staticmethod
    def show_ip_interface_brief(xgw_name):
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        return XgwManagement.show_ip_interface_brief(xgw_dut)

    @staticmethod
    def dpi_rule_actived(xgw_name):
        logger.info('start dpi rule active...')
        t1 = time.time()
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        xgw_config = XgwService.find_xgw_config(xgw_name)
        logger.info('  dpi file: {0}'.format(xgw_config.dpi_file))
        XgwManagement.dpi_rule_actived(xgw_dut, xgw_config.dpi_file)
        logger.info('end dpi rule active, {0}s'.format(time.time() - t1))

    @staticmethod
    def check_interface_status(xgw_name, port_status_before_upgrade):
        logger.info('start check interface status...')
        t1 = time.time()
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        xgw_config = XgwService.find_xgw_config(xgw_name)
        XgwManagement.check_interface_status(xgw_dut, port_status_before_upgrade, xgw_config.port_status_check_max_time)
        logger.info('end check interface status, {0}s'.format(time.time() - t1))

    @staticmethod
    def create_xgw_dut(xgw_name, host, port, user_name, password):
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        if not xgw_dut:
            xgw_dut = Xgw(host, port, user_name, password)
        if not xgw_dut.login():
            raise Exception(
                "cannot connect to ip = {0}".format(host))

        TelnetRepository().add(xgw_name, xgw_dut)
        return xgw_dut

    @staticmethod
    def find_xgw_dut(xgw_name):
        return TelnetRepository().find(xgw_name)

    @staticmethod
    def release_xgw_dut():
        for k, v in TelnetRepository().items():
            v.logout()

    @staticmethod
    def create_xgw_config(xgw_name, xgw_config):
        xgw_config_obj = XgwService.find_xgw_config(xgw_name)
        if not xgw_config_obj:
            xgw_config_obj = XgwConfig(xgw_config)
            ConfigRepository().add(xgw_name, xgw_config_obj)
        return xgw_config_obj

    @staticmethod
    def find_xgw_config(name):
        return ConfigRepository().find(name)

    @staticmethod
    def get_show_running_and_save(xgw_name, upgrade):
        t = time.time()
        upgrade = int(upgrade)
        logger.info("start get show running...")
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        xgw_config = XgwService.find_xgw_config(xgw_name)
        show_running_file = xgw_config.get_show_running_file(upgrade)
        XgwShowRunning.get_show_running_and_save(xgw_dut, show_running_file)
        logger.info('show running save to {0}'.format(show_running_file))
        logger.info('end get show running, {0}s'.format(time.time() - t))
        return show_running_file

    @staticmethod
    def analysis_show_running_by_apn_and_save(show_running_file,analysis_show_running_file):
        XgwShowRunning.analysis_show_running_by_apn_and_save(show_running_file,analysis_show_running_file)
        logger.info('show running analysis result save to {0}'.format(analysis_show_running_file))

    @staticmethod
    def sort_show_running_and_save(show_running_file):
        XgwManagement.sort_show_running_cmd(str(show_running_file))

    @staticmethod
    def get_run_save_path(xgw_name):
        xgw_config = XgwService.find_xgw_config(xgw_name)
        return xgw_config.run_save_path

    @staticmethod
    def xgw_filter_pstt_by_show_running_config(xgw_name, pstt_name):
        from testlib.service.EngineProxyService import EngineProxyService
        xgw_config = XgwService.find_xgw_config(xgw_name)
        analysis_running_file = xgw_config.analysis_show_running_file_0
        soft_para_file = xgw_config.soft_para_file_0
        return EngineProxyService.filter_pstt_by_show_running_config(pstt_name,
                                                                     analysis_running_file,
                                                                     soft_para_file)

    @staticmethod
    def xgw_classify_show_running_config_by_cases(xgw_name, pstt_name):
        from testlib.service.EngineProxyService import EngineProxyService
        xgw_config = XgwService.find_xgw_config(xgw_name)
        local_path = xgw_config.run_save_path
        analysis_running_file = xgw_config.analysis_show_running_file_0
        soft_para_file = xgw_config.soft_para_file_0
        return EngineProxyService.classify_show_running_config_by_cases(pstt_name,
                                                                        analysis_running_file,
                                                                        soft_para_file)

    @staticmethod
    def get_and_analysis_show_running(xgw_name, upgrade):
        upgrade = int(upgrade)
        xgw_config = XgwService.find_xgw_config(xgw_name)
        XgwService.get_show_running_and_save(xgw_name, upgrade)
        show_running_file = xgw_config.get_show_running_file(upgrade)
        XgwService.analysis_show_running_by_apn_and_save(show_running_file,
                                                        xgw_config.get_analysis_show_running_file(upgrade))
        return show_running_file

    @staticmethod
    def get_and_save_soft_para(xgw_name, upgrade):
        logger.info('get_and_save_soft_para...')
        upgrade = int(upgrade)
        xgw_config = XgwService.find_xgw_config(xgw_name)
        xgw_dut = XgwService.find_xgw_dut(xgw_name)
        XgwSoftPara.get_and_save_soft_para_to_file(xgw_dut,
                                                   xgw_config.get_soft_para_file(upgrade))
