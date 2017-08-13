# coding:utf-8
from robot.api import logger
import os
from testlib.infrastructure.utility.FileOperation import FileOperation


class XgwConfig(object):
    def __init__(self, xgw_config):
        self._xgw_config = xgw_config
        self._check()

        self.host = xgw_config[1]
        self.telnet_user_name = xgw_config[3]
        self.telnet_password = xgw_config[5]
        self.local_save_path = xgw_config[7]
        self.new_version_in_local = xgw_config[9]
        self.ftp_user_name_of_version_server = xgw_config[11]
        self.ftp_password_of_version_server = xgw_config[13]
        self.ftp_host_of_version_server = xgw_config[15]
        self.relative_path_of_target_version_set_in_ftp = xgw_config[17]
        self.target_version_set_name = xgw_config[19]
        self.dpi_file = xgw_config[21]
        self.pgw_cpu_restart_max_time = int(xgw_config[23])
        self.port_status_check_max_time = int(xgw_config[25])
        self.is_en = int(xgw_config[27].lower() == 'en')

        self.output_dir = ''
        self.run_save_path = ''
        self.dir_before_upgrade = ''
        self.dir_after_upgrade = ''
        self.local_backup_zdb_path = ''
        self.sigtrace_path_0 = ''
        self.sigtrace_path_1 = ''

        self.show_running_file_0 = ''
        self.show_running_file_1 = ''
        self.analysis_show_running_file_0 = ''
        self.analysis_show_running_file_1 = ''
        self.soft_para_file_0 = ''
        self.soft_para_file_1 = ''

        self.create_default_dir()

    def get_soft_para_file(self,upgrade):
        if upgrade:
            return self.soft_para_file_1
        return self.soft_para_file_0

    def get_show_running_file(self,upgrade):
        if upgrade:
            return self.show_running_file_1
        return self.show_running_file_0

    def get_analysis_show_running_file(self,  upgrade):
        if upgrade:
            return self.analysis_show_running_file_1
        else:
            return self.analysis_show_running_file_0

    def current_local_save_path(self, upgrade):
        if upgrade:
            return self.dir_after_upgrade
        return self.dir_before_upgrade

    def show_running_path(self, upgrade):
        return '{0}/showrunning'.format(self.current_local_save_path(upgrade))

    # def set_upgrade(self, value = True):
    #     self.is_upgraded = value

    def create_default_dir(self):
        if not os.path.exists(self.local_save_path):
            raise Exception('local save path {0} not exists, please create it first'.format(self.local_save_path))

        self.run_save_path = '{0}/{1}'.format(self.local_save_path, FileOperation.get_file_name_of_current_time())
        FileOperation.create_directory(self.run_save_path)
        self.create_before_upgrade_dir(self.run_save_path)
        self.create_after_upgrade_dir(self.run_save_path)
        self.create_output_dir(self.run_save_path)

    def create_before_upgrade_dir(self, run_save_path):
        self.dir_before_upgrade = "{0}/before_upgrade".format(run_save_path)
        FileOperation.create_directory(self.dir_before_upgrade)

        self.local_backup_zdb_path = "{0}/backup_zdb".format(self.dir_before_upgrade)
        FileOperation.create_directory(self.local_backup_zdb_path)

        show_running_path = "{0}/showrunning".format(self.dir_before_upgrade)
        FileOperation.create_directory(show_running_path)

        self.sigtrace_path_0 = '{0}/sigtrace'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.sigtrace_path_0)

        self.show_running_file_0  = "{0}/show_running.txt".format(show_running_path)
        self.analysis_show_running_file_0 = "{0}/show_running_analysis_result.txt".format(show_running_path)
        self.soft_para_file_0 = "{0}/soft_para.txt".format(self.dir_before_upgrade);

    def create_after_upgrade_dir(self, run_save_path):
        self.dir_after_upgrade = "{0}/after_upgrade".format(run_save_path)
        FileOperation.create_directory(self.dir_after_upgrade)

        show_running_path = "{0}/showrunning".format(self.dir_after_upgrade)
        FileOperation.create_directory(show_running_path)

        self.sigtrace_path_1 = '{0}/sigtrace'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.sigtrace_path_1)

        self.show_running_file_1  = "{0}/show_running.txt".format(show_running_path)
        self.analysis_show_running_file_1 = "{0}/show_running_analysis_result.txt".format(show_running_path)
        self.soft_para_file_1 = "{0}/soft_para.txt".format(self.dir_after_upgrade);

    def create_output_dir(self, run_save_path):
        self.output_dir = "{0}/output".format(run_save_path)
        FileOperation.create_directory(self.output_dir)

    def _check(self):
        num = len(self._xgw_config)
        for i in range(1, num)[::2]:
            if i == 5:  # 密码允许为空
                continue
            if len(self._xgw_config[i]) == 0:
                raise Exception("value of {0} is empty, invalid!".format(self._xgw_config[i - 1]))

    def print_config(self):
        num = len(self._xgw_config)
        logger.info("xgw config:")
        for i in range(0, num)[::2]:
            logger.info(u'  {0:<40}{1:<40}'.format(self._xgw_config[i], self._xgw_config[i + 1]))
