# coding:utf-8
import os
import time
import re
from robot.output import LOGGER
from testlib.infrastructure.channels.ftp.ftpsync import FTPSync
from testlib.infrastructure.foreigntool.showrunningcmdsort import ShowRunningCommandSort


class XgwManagement(object):
    @staticmethod
    def backup_zdb(xgw_config):
        local_path = xgw_config.local_backup_zdb_path
        if not os.path.isdir(local_path):
            raise Exception("{0} is not directory!".format(local_path))
        if not os.path.exists(local_path):
            raise Exception("{0} is not exists!".format(local_path))

        download_dirs = ['xgwconfig', 'DATA0', 'config', 'vmm', 'DPI']
        f = FTPSync(xgw_config.host, xgw_config.telnet_user_name, xgw_config.telnet_password)
        f.download(local_path, download_dirs)
        f.close()

    @staticmethod
    def check_mpu(xgw_dut):
        cmd = 'show synchronization'
        xgw_dut.login()
        xgw_dut.excute_channel_cmd('end', '#', 10)
        cmd_result = xgw_dut.excute_channel_cmd(cmd, '#', 10)
        temp = cmd_result.return_string[
               cmd_result.return_string.find('LE             Location            Status         Sync-state'):]
        if temp.find('Slave') > 0:
            LOGGER.error("{0}".format(temp))
            raise Exception(u'先拔出备板后，再升级')
        else:
            LOGGER.info(u'mpu正常, 可以升级')
        xgw_dut.logout()

    @staticmethod
    def set_version_start_style(xgw_dut):
        cmd_list = ['end',
                    'conf t',
                    'nvram imgfile-location local',
                    'end']
        xgw_dut.login()
        for cmd in cmd_list:
            xgw_dut.excute_channel_cmd(cmd, '#', 10)
        xgw_dut.logout()

    @staticmethod
    def upload_new_zdb(xgw_config, local_zdb_path, remote_zdb_path):
        f = FTPSync(xgw_config.host, xgw_config.telnet_user_name, xgw_config.telnet_password)
        f.upload(local_zdb_path, remote_zdb_path)
        f.close()

    @staticmethod
    def load_new_version(xgw_dut, xgw_config):
        cmd_list = ['end',
                    'conf t',
                    'nvram boot-username {0}'.format(xgw_config.ftp_user_name_of_version_server),
                    'nvram boot-password {0}'.format(xgw_config.ftp_password_of_version_server),
                    'nvram boot-server {0}'.format(xgw_config.ftp_host_of_version_server),
                    'nvram ftp-path {0}'.format(xgw_config.relative_path_of_target_version_set_in_ftp),
                    'nvram imgfile-location network {0}'.format(xgw_config.target_version_set_name),
                    'nvram default-gateway 10.42.184.1'
                    ]
        xgw_dut.login()
        for cmd in cmd_list:
            xgw_dut.excute_channel_cmd(cmd, '#', 10)
        xgw_dut.logout()

    @staticmethod
    def restart_fore_version(xgw_dut):
        xgw_dut.login()
        xgw_dut.excute_channel_cmd('end', '#', 2)
        cmd_result = xgw_dut.excute_channel_cmd('reload system force', ']:', 5)
        try:
            xgw_dut.excute_channel_cmd('y', '#', 2)
        except:
            pass
        xgw_dut.logout()

    @staticmethod
    def check_pgw_cpu_restart(xgw_dut, before_show_group, timeout):
        t1 = time.time()
        if timeout < 60:
            timeout = 60
        dict_cpu_info_before_upgrade = XgwManagement._analysis_show_group(before_show_group)
        xgw_dut.login()
        while True:
            after_show_group = XgwManagement.show_pgw_group(xgw_dut)
            dict_cpu_info_after_upgrade = XgwManagement._analysis_show_group(after_show_group)
            if len(dict_cpu_info_after_upgrade) > 0:
                for cpu_location, status in dict_cpu_info_after_upgrade.items():
                    if dict_cpu_info_before_upgrade[cpu_location] == 'unknown':
                        continue
                    if status in ['master', 'slave'] \
                            and dict_cpu_info_before_upgrade[cpu_location] in ['master', 'slave']:
                        continue
                    break
                else:
                    break
            if time.time() - t1 >= timeout:
                raise Exception(
                    'pgw cpu restart false. before upgrade is {0};after is {1}'.format(before_show_group,
                                                                                       after_show_group))
            time.sleep(60)
        xgw_dut.logout()

    @staticmethod
    def dpi_rule_actived(xgw_dut, dpi_file):
        xgw_dut.login()
        cmd_list = ['end',
                    'conf t',
                    'xgw',
                    'pgw',
                    'dpi-file activate {0}'.format(dpi_file)]
        for cmd in cmd_list:
            try:
                xgw_dut.excute_channel_cmd(cmd, '#', 2 * 60)
            except:
                pass
        time.sleep(60)
        max_num = 5
        while max_num:
            dpi_files = XgwManagement._get_dpi_files(xgw_dut)
            if dpi_file in dpi_files:
                break
            time.sleep(60)
            max_num -= 1
        else:
            raise Exception('dpi rule actived fail')

        xgw_dut.excute_channel_cmd('end', '#', 5)
        xgw_dut.excute_channel_cmd('write', '#', 5 * 60)

    @staticmethod
    def check_interface_status(xgw_dut, port_status_before_upgrade, timeout):
        if timeout < 60:
            timeout = 60
        t = time.time()
        dict_port_status_before_upgrade = XgwManagement._analysis_port_status(port_status_before_upgrade)
        while True:
            port_status_after_upgrade = XgwManagement.show_ip_interface_brief(xgw_dut)
            dict_port_status_after_upgrade = XgwManagement._analysis_port_status(port_status_after_upgrade)
            if XgwManagement._is_port_status_equals(dict_port_status_before_upgrade, dict_port_status_after_upgrade):
                break
            if time.time() - t >= timeout:
                raise Exception("check port status fail,"
                                "port status before upgrade is {0}; now is {1}".format(port_status_before_upgrade,
                                                                                       port_status_after_upgrade))
            time.sleep(60)

    @staticmethod
    def _is_port_status_equals(dict_port_status1, dict_port_status2):
        for name, status in dict_port_status1.items():
            status2 = dict_port_status2.get(name, [])
            if status != status2:
                return False
        return True

    @staticmethod
    def _get_dpi_files(xgw_dut):
        try:
            cmd_result = xgw_dut.excute_channel_cmd('show pgw cpu-dpi-info', '#', 5)
            return_string = cmd_result.return_string
            LOGGER.debug("show pgw cpu-dpi-info:{0}".format(return_string))
            return XgwManagement._extract_dpi_files(return_string)
        except:
            return []
        # dpi_files = []
        # pattern = '^\s+(\w+.bin)'
        # result = re.findall(pattern, return_string, re.MULTILINE)
        # if not result:
        #     pattern = '([^\s]+.bin)'
        #     result = re.findall(pattern, return_string, re.MULTILINE)
        #     if result:
        #         dpi_files = result
        # else:
        #     pattern = '(DPI_\w+)|(\w+.bin)'
        #     result = re.findall(pattern, return_string, re.MULTILINE)
        #     if result:
        #         for i in range(0, len(result))[::2]:
        #             dpi_files.append('{0}{1}'.format(result[i][0], result[i + 1][1]))
        # return dpi_files

    @staticmethod
    def _extract_dpi_files(dpi_file_content):
        dpi_file_content = dpi_file_content[dpi_file_content.find('DPI'):]
        lines = dpi_file_content.splitlines()
        name_split = False
        dpi_file_list = []
        for line in lines:
            if line.endswith('#'):
                continue
            line = line.strip(' ')
            if not line:
                continue
            if name_split:
                dpi_file_list[-1] += line
                name_split = False
                continue
            if line.find('DPI') >= 0:
                dpi_file = line[line.find('DPI'):].split(' ')[0]
            else:
                dpi_file = line
            dpi_file_list.append(dpi_file)

            name_split = not dpi_file.endswith('.bin')
        return dpi_file_list

    @staticmethod
    def show_pgw_group(xgw_dut):
        xgw_dut.login()
        xgw_dut.excute_channel_cmd('end', '#', 5)
        cmd_result = xgw_dut.excute_channel_cmd('show pgw group', '#', 5)
        xgw_dut.logout()
        return cmd_result.return_string

    @staticmethod
    def show_ip_interface_brief(xgw_dut):
        xgw_dut.login()
        xgw_dut.excute_channel_cmd('end', '#', 5)
        cmd_result = xgw_dut.excute_channel_cmd('show ip interface brief', '#', 5)
        xgw_dut.logout()
        return cmd_result.return_string

    @staticmethod
    def _analysis_show_group(show_group_result):
        pattern = '\d+\s+(\d+/\d+/\d+)\s*\w+\s*\d+\s*(\w+)'
        result = re.findall(pattern, show_group_result)
        dict_cpu_info = {}
        for cpu_info in result:
            dict_cpu_info[cpu_info[0]] = cpu_info[1]
        return dict_cpu_info

    @staticmethod
    def _analysis_port_status(port_status):
        pattern = '([^\s]+)\s+[^\s]+\s+[^\s]+\s+(\w+)\s+(\w+)\s+(\w+)'
        result = re.findall(pattern, port_status)
        dict_port_status = {}
        for status in result:
            dict_port_status[status[0]] = [status[1], status[2], status[3]]
        return dict_port_status

    @staticmethod
    def sort_show_running_cmd(show_running_file):
        cmd_sort = ShowRunningCommandSort(show_running_file)
        if cmd_sort.sort_cmd():
            LOGGER.info('sort show running command success')
        else:
            LOGGER.error('sort show running command fail')
        cmd_sort.release()


if __name__ == '__main__':
    show_running_file = r'D:\xgw_project_valid\20160715_105200\before_upgrade\showrunning\show_running.txt'
    out_file =r'D:\xgw_project_valid\20160715_105200\before_upgrade\showrunning\result.log'
    XgwManagement.analysis_show_running_by_apn_and_save(show_running_file,out_file)
    #dict_apn = XgwManagement.analysis_show_running_by_apn_and_save(show_running_file)
##    with open(r"D:\xgw_project_valid\show_running_analysis_result.txt",'w') as f:
##        f.write(str(dict_apn))
##    from  testlib.infrastructure.device.xgw.Xgw import Xgw
##
##    # XgwManagement.analysis_show_running_by_apn_and_save(r'E:\linxing\iTest\branches\code\iTest\RIDE-1.4_1119\robot\temp\show_running.txt')
##    xgw_dut = Xgw('10.42.188.56')
##    # # cmd = 'show pgw cpu-dpi-info'
##    # cmd = 'write'
##    xgw_dut.login()
##
##    dpi_file_content ='''GroupNo   Cpu-state      Dpi-file-name     Status
##3         slave          DPI_GSU_201409041 activated
##                         55154.bin
##1         slave          DPI_GSU_201409041 activated
##                         55154.bin
##1         master         DPI_GSU_201409041 activated
##                         55154.bin
##2         slave          DPI_GSU_201409041 activated
##                         55154.bin
##3         master         DPI_GSU_201409041 activated
##                         55154.bin
##2         master         DPI_GSU_201409041 activated
##                         55154.bin
##            '''
##    print XgwManagement._extract_dpi_files(dpi_file_content)
##
##    dpi_file_content = '''ShelfNo  SlotNo  CpuNo  Dpi-file-name     Status
##0        2       3      DPI_GSU_201509.bin activated
##
##0        2       3      DPI_GSU_201509.bin activated
##'''
##    print XgwManagement._extract_dpi_files(dpi_file_content)
##    dpi_file_content = '''ShelfNo  SlotNo  CpuNo  Dpi-file-name     Status
##0        2       3      DPI_GSU_201509 activated
##                        211.bin
##0        2       3      DPI_GSU_201509 activated
##                        221.bin'''
##    print XgwManagement._extract_dpi_files(dpi_file_content)
##    dpi_file_content = '''ShelfNo  SlotNo  CpuNo  Dpi-file-name     Status
##0        2       3      DPI_GSU_201509211.b activated
##                        in
##0        2       3      DPI_GSU_201509211.b activated
##                        in'''
##    print XgwManagement._extract_dpi_files(dpi_file_content)
##    dpi_file_content = '''ShelfNo  SlotNo  CpuNo  Dpi-file-name     Status
##0        2       3      DPI_GSU_201509211.bi activated
##                        n
##0        2       3      DPI_GSU_201509211.bi activated
##                        n'''
##    print XgwManagement._extract_dpi_files(dpi_file_content)
##    dpi_file_content = '''ShelfNo  SlotNo  CpuNo  Dpi-file-name     Status
##0        2       3      DPI_GSU_201509211 activated
##                        .bin
##0        2       3      DPI_GSU_201509211 activated
##                        .bin'''
##    print XgwManagement._extract_dpi_files(dpi_file_content)
    #print XgwManagement._extract_dpi_files('')
    # cmd_list = ['con t',
    #             'ftp-server enable',
    #             'ftp-server top-directory /sysdisk0/',
    #             'load-mode txt',
    #             'end']
    # for cmd in cmd_list:
    #     xgw_dut.excute_channel_cmd(cmd, '#', 10)
    # cmd_result = xgw_dut.excute_channel_cmd('write', '#', 120)
    # print cmd_result.return_string
    # print XgwManagement._get_dpi_files(xgw)

    #     pattern = '^\s+(\w+.bin)'
    #     return_string = '''show pgw cpu-dpi-info
    # ShelfNo  SlotNo  CpuNo  Dpi-file-name     Status
    # 0        2       3      DPI_GSU_201509211 activated
    #                         64441.bin
    # 0        2       0      DPI_GSU_201509211 activated
    #                         64441.bin
    # 0        2       2      DPI_GSU_201509211 activated
    #                         64441.bin
    # 0        2       1      DPI_GSU_201509211 activated
    #                         64441.bin
    # Auto-GUL56#'''
    #     result = re.findall(pattern, return_string,re.MULTILINE)
    #     print result
