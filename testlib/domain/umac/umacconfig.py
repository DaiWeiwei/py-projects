# coding:utf-8
from robot.api import logger
import os
import re
from testlib.infrastructure.utility.FileOperation import FileOperation

class UmacConfig(object):
    def __init__(self, umac_config):
        self._umac_config = umac_config
        self._check()
        self.host = re.findall('\d+\.\d+\.\d+\.\d+',umac_config[1])[0]
        self.office_id = int(re.findall('\_\d+',umac_config[1])[0].replace('_',''))
        self.system_user_name = 'root'
        self.system_password = umac_config[3].strip()
        self.telnet_user_name = 'admin'
        self.telnet_password = umac_config[5].strip()
        self.telnet_port = 7722
        self.src_ind_board_version_path = umac_config[7].strip()
        self.dst_ind_board_version_path = '/home/ngomm/'+umac_config[1].split('/')[3]+'/cncmmverfile'
        self.src_service_version_path = umac_config[9].strip()
        self.dst_service_version_path = '/home/ngomm/'+umac_config[1].split('/')[3]+'/cnvmverfile'
        self.syna_sleep_time = 600 #固定写死，实际上已经没用，int(umac_config[11]) if len(umac_config[11]) > 0 else 120
        self.omm_version_path = umac_config[11]
        self.ser_version_no =  umac_config[13].strip()
        self.omm_url = umac_config[1].strip()
        self.rule_file = umac_config[15].strip()
        self.local_save_path = umac_config[17].strip()
        self.is_en = int(umac_config[19].strip().lower() == 'en')
        self.netypeid=umac_config[1].split('/')[3]
        self.lice_upgrade=umac_config[21].strip().lower()
        self.src_omm_version_no = umac_config[23].strip()
        self.src_omm_path = umac_config[25].strip()
        self.restored_data = umac_config[27].strip()

        #self.is_upgraded = False
        self.run_save_path = ''
        self.dir_before_upgrade = ''
        self.dir_after_upgrade = ''
        self.local_backup_zdb_path_0 = ''
        self.local_backup_zdb_path_1 = ''
        self.output_dir = ''
        # self.compared_sig_dir = ''
        self.cmd_config_html_dir_0 = ''
        self.cmd_config_html_dir_1 = ''
        self.sigtrace_path_0 = ''
        # self.signal_wash_path_0 = ''
        self.sigtrace_path_1 = ''
        # self.signal_wash_path_1 = ''
        # self.filters_dir = ''
        self.alarm_path_0 = ''
        self.alarm_path_1 = ''
        self.memory_path_0 = ''
        self.memory_path_1 = ''
        self.license_path_0 = ''
        self.license_path_1 = ''
        self.performance_path_0 = ''
        self.performance_path_1 = ''
        self.log_path = ''
        self.temp_output_path = ''
        self._2g = True
        self._3g = True
        self._4g = True

        if self.office_id<250:  #250之后不创建存储目录，该局专门用于验证license，这个局号外场不可能存在的。
            self.create_default_dir()
            self.check_licfile()
    def check_licfile(self):
        lcs_num=0
        if self.lice_upgrade=='y':
            for filename in os.listdir(self.local_save_path):
              if filename.endswith('.lic'):
                lcs_num+=1
            if lcs_num>1 or lcs_num==0 :
              raise Exception(u'设置为升级后要更换license，但是'+self.local_save_path+u'目录下无更换的license文件或者多于1个license文件')

    def current_local_save_path(self,upgrade):
        if upgrade:
            return self.dir_after_upgrade
        return self.dir_before_upgrade

    def cmd_config_html_dir(self, upgrade):
        if upgrade:
            return self.cmd_config_html_dir_1
        return self.cmd_config_html_dir_0
    def cmd_config_backupdata(self, upgrade):
        if upgrade:
            return self.local_backup_zdb_path_1
        return self.local_backup_zdb_path_0

    def cmd_alarm_dir(self, upgrade):
        if upgrade:
            return self.alarm_path_1
        return self.alarm_path_0

    def cmd_performance_dir(self, upgrade):
        if upgrade:
            return self.performance_path_1
        return self.performance_path_0

    def cmd_memory_dir(self, upgrade):
        if upgrade:
            return self.memory_path_1
        return self.memory_path_0

    def cmd_sigtrace_dir(self, upgrade):
        if upgrade:
            return self.sigtrace_path_1
        return self.sigtrace_path_0

    def cmd_license_dir(self, upgrade):
        if upgrade:
            return self.license_path_1
        return self.license_path_0
    @property
    def office_name(self):
        try:
            #http://195.137.81.55:2323/combo_mmegngp_sgsn_28/client/#
            #http://192.0.19.10:2323/mme_19/client/#
            #http://195.137.81.55:2323/gngp_sgsn_27/client/#
            #get [combo_mmegngp_sgsn_28]
            return self.omm_url.split("/")[3]
        except:
            return ''
    @property
    def ne_type(self):
        office_name = self.office_name.lower()
        try:
            if 'combo_' in office_name:
                return 'COMBO'
            if 'mme_' in office_name:
                return 'MME'
            if 'sgsn_' in office_name:
                return 'SGSN'
            return ''
        except:
            return ''
    # def set_upgrade(self,value):
    #     self.is_upgraded = value

    def create_default_dir(self):
        if not os.path.exists(self.local_save_path):
            raise Exception('local save path {0} not exists, please create it first'.format(self.local_save_path))

        self.run_save_path = '{0}/{1}'.format(self.local_save_path,
                                                  self.office_name)
        FileOperation.create_directory(self.run_save_path)

        # self.filters_dir = os.path.join(self.local_save_path, 'filters')
        # FileOperation.create_directory(self.filters_dir)

        self.log_path = '{0}/log'.format(self.local_save_path)
        FileOperation.create_directory(self.log_path)

        FileOperation.create_directory(self.run_save_path)
        self.create_before_upgrade_dir(self.run_save_path)
        self.create_after_upgrade_dir(self.run_save_path)
        self.create_output_dir(self.run_save_path)

    def create_output_dir(self, run_save_path):
        self.output_dir = "{0}/output".format(run_save_path)
        FileOperation.create_directory(self.output_dir)

        # self.compared_sig_dir = "{0}/compared sigtrace".format(self.output_dir)
        # FileOperation.create_directory(self.compared_sig_dir)

        self.temp_output_path = '{0}/temp_output'.format(self.run_save_path)
        FileOperation.create_directory(self.temp_output_path)

    def create_before_upgrade_dir(self, run_save_path):
        self.dir_before_upgrade = "{0}/before_upgrade".format(run_save_path)
        FileOperation.create_directory(self.dir_before_upgrade)

        self.local_backup_zdb_path_0 = "{0}/backup_zdb".format(self.dir_before_upgrade)
        FileOperation.create_directory(self.local_backup_zdb_path_0)

        self.cmd_config_html_dir_0 = '{0}/html'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.cmd_config_html_dir_0)

        self.sigtrace_path_0 = '{0}/sigtrace'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.sigtrace_path_0)

        # self.signal_wash_path_0 = '{0}/after wash'.format(self.sigtrace_path_0)
        # FileOperation.create_directory(self.signal_wash_path_0)

        self.alarm_path_0 = '{0}/alarm'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.alarm_path_0)

        self.performance_path_0 = '{0}/performance'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.performance_path_0)

        self.memory_path_0 = '{0}/memory'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.memory_path_0)

        self.license_path_0 = '{0}/license'.format(self.dir_before_upgrade)
        FileOperation.create_directory(self.license_path_0)

    def create_after_upgrade_dir(self, run_save_path):
        self.dir_after_upgrade = "{0}/after_upgrade".format(run_save_path)
        FileOperation.create_directory(self.dir_after_upgrade)

        self.cmd_config_html_dir_1 = '{0}/html'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.cmd_config_html_dir_1)

        self.sigtrace_path_1 = '{0}/sigtrace'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.sigtrace_path_1)

        # self.signal_wash_path_1 = '{0}/after wash'.format(self.sigtrace_path_1)
        # FileOperation.create_directory(self.signal_wash_path_1)

        self.local_backup_zdb_path_1 = '{0}/backup_zdb'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.local_backup_zdb_path_1)

        self.alarm_path_1 = '{0}/alarm'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.alarm_path_1)

        self.performance_path_1 = '{0}/performance'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.performance_path_1)

        self.memory_path_1 = '{0}/memory'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.memory_path_1)

        self.license_path_1 = '{0}/license'.format(self.dir_after_upgrade)
        FileOperation.create_directory(self.license_path_1)

    def delete_allfiles(self, run_save_path):
        FileNames=os.listdir(run_save_path)
        if (len(FileNames)>0):
          for fn in FileNames:
            #删除该目录下所有文件
            fullfilename=os.path.join(run_save_path,fn)
            os.remove(fullfilename)
    def check_files(self, run_save_path):
        FileNames=os.listdir(run_save_path)
        if (len(FileNames)==0):
            return False
        else :
            return True
    def _check(self):
        num = len(self._umac_config)
        for i in range(1, num)[::2]:
            if i == 5:  # 密码允许为空
                continue
            if len(self._umac_config[i]) == 0:
                raise Exception("value of {0} is empty, invalid!".format(self._umac_config[i - 1]))

    def set_ne_generation(self,_2g,_3g,_4g):
        self._2g = _2g
        self._3g = _3g
        self._4g = _4g

    def is_combo(self):
        return self.ne_type.lower() == 'combo'

    def can_sgsn_upgrade(self):
        if not self.is_combo():
            return True
        #如果是combo局
        #如果2g,3g同时没有，则返回false
        if not self._2g and not self._3g:
            return False
        return True

    def can_mme_upgrade(self):
        if not self.is_combo():
            return True
        #如果是combo局
        #如果4g没有，则返回false
        if not self._4g:
            return False
        return True


    def print_config(self):
        num = len(self._umac_config)
        logger.info("umac config:")
        for i in range(0, num)[::2]:
            logger.info('  %-40s%-40s' % (self._umac_config[i], self._umac_config[i + 1]))
