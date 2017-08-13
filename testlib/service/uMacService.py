# coding:utf-8
import re
import os
import time
from robot.api import logger
from testlib.domain.umac.uMacGetAlarmData import GetAlarmData
from testlib.domain.umac.get_pm_task import get_pm_task
from testlib.domain.umac.installomm import Installomm
#from testlib.domain.umac.FunctionAnalysis import FunctionAnalysis
from testlib.domain.umac.uMacOmm import UmacOmm
from testlib.infrastructure.device.umac.umac import uMac
from testlib.domain.ne.ConfigRepository import ConfigRepository
from testlib.domain.umac.umacconfig import UmacConfig
from testlib.domain.umac.OmmRepository import OmmRepository
from testlib.domain.TelnetRepository import TelnetRepository
from testlib.domain.umac.independentboard.independentboardmanagement import IndependentBoardManagement
from testlib.domain.umac.serviceversionmanagement import ServiceVersionManagement
from testlib.domain.umac.configcommandhtml.configcommandhtml import ConfigCommandHtml
from testlib.infrastructure.iecapture.iecapture import IeCapture
from testlib.domain.umac.umacBoardstatusinfo import umacBoardstatusinfo
from testlib.domain.umac.ComparisionService import ComparisionService
from testlib.domain.umac.umaclicensetest import umaclicensetest
from testlib.service.DataAnalysisService import DataAnalysisService
from testlib.domain.umac.uMacLicense import uMacLicense
from testlib.domain.umac.negeneration import NeGeneration
upgrade_ind_boards = []


class uMacService:
    @staticmethod
    def init_umac(umac_name, **_umac_config):
        umac_config = _umac_config['**_umac_config']
        umac_config_obj = uMacService.create_umac_config(umac_name, umac_config)
        umac_config_obj.print_config()


        uMacService.create_umac_dut(umac_name,
                                       umac_config_obj.host,
                                       umac_config_obj.telnet_port,
                                       umac_config_obj.telnet_user_name,
                                       umac_config_obj.telnet_password,
                                       umac_config_obj.office_id
                                     )

        uMacService.create_umac_omm(umac_name,
                                    umac_config_obj.host,
                                    umac_config_obj.system_user_name,
                                    umac_config_obj.system_password)

    @staticmethod
    def release_umac_service():
        uMacService.release_umac_dut()

    @staticmethod
    def create_umac_dut(umac_name, host, port, user_name, password, office_id):
        umac_dut_name = '{0}_{1}'.format(umac_name, office_id)
        umac_dut = uMacService.find_umac_dut(umac_name, office_id)
        if not umac_dut:
            umac_dut = uMac(host, port, user_name, password, office_id)
            TelnetRepository().add(umac_dut_name, umac_dut)
        if not umac_dut.login_clean():
            raise Exception(
                "cannot connect to ip = {0},office id = {1}".format(host, office_id))

        return umac_dut

    @staticmethod
    def find_umac_dut(umac_name, office_id):
        umac_dut_name = '{0}_{1}'.format(umac_name, office_id)
        return TelnetRepository().find(umac_dut_name)

    @staticmethod
    def release_umac_dut():
        for k, v in TelnetRepository().items():
            v.logout()

    @staticmethod
    def create_umac_omm(umac_name, host, user_name, password):
        omm = uMacService.find_umac_omm(umac_name)
        if not omm:
            omm = UmacOmm(host, user_name, password)
            OmmRepository().add(umac_name, omm)
        return omm

    @staticmethod
    def find_umac_omm(umac_name):
        return OmmRepository().find(umac_name)

    @staticmethod
    def release_umac_omm():
        for k, v in OmmRepository().items():
            v.close()

    @staticmethod
    def create_umac_config(umac_name, umac_config):
        umac_config_obj = uMacService.find_umac_config(umac_name)
        if not umac_config_obj:
            umac_config_obj = UmacConfig(umac_config)
            ConfigRepository().add(umac_name, umac_config_obj)
        return umac_config_obj

    @staticmethod
    def find_umac_config(umac_name):
        return ConfigRepository().find(umac_name)

    @staticmethod
    def install_omm(umac_name):
        time_start = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        office_id = umac_config.office_id
        logger.info("start installing omm:name = {0},office_id = {1}".format(umac_name, office_id))
        omm = uMacService.find_umac_omm(umac_name)
        omm.install_omm(office_id,umac_config.omm_version_path)

    @staticmethod
    def upgrade_omm(umac_name,office_id):
        time_start = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        if not office_id:
            office_id = umac_config.office_id
        logger.info("start upgrade omm:name = {0},office_id = {1}".format(umac_name, office_id))

##        umac_dut = uMacService.create_umac_dut(umac_name,
##                                               umac_config.host,
##                                               umac_config.telnet_port,
##                                               umac_config.telnet_user_name,
##                                               umac_config.telnet_password,
##                                               office_id)
##        umac_dut.logout()
        omm = uMacService.find_umac_omm(umac_name)
        omm.upgrade_omm_agent_and_version(office_id,umac_config.omm_version_path)
        #logger.info('wait for 300s, and then check if omm is upgraded')
        #time.sleep(300)
        #检查升级后版本是否一致,本地网管版本信息获取
        ommlocal_path=umac_config.omm_version_path
        for filename in os.listdir(ommlocal_path):
            if filename.startswith('ZXUN_uMAC(OMM)'):
##                ommvn=re.findall('(\V\d\.\d+.\d+\.\w*\.*\w*)_\w*_\w*',filename)
##                ommlocal_verion=ommvn[0].lower()
                ommvn=filename.split('_')[2]
                ommlocal_verion=ommvn.lower()   #用下划线分割获取版本

                break
        #网管服务器升级后的版本获取
        vercmd='find /home/ngomm/'+umac_config.omm_url.split('/')[3]+'/client/pub/main/ -type f -name "main-frame-config.xml"  | xargs grep  "verShow"'
        ommupd_version=omm._get_omm_version_no(vercmd)
        logger.info(u'升级后版本：'+ommupd_version+u'目标版本：'+ommlocal_verion)
        if ommlocal_verion!=ommupd_version.lower():
            raise Exception(u'升级后的网管版本和目标版本不一致，升级流程终止！')
        logger.info("end upgrade omm:name = {0},"
                    "office_id = {1},elapse = {2}s"
                    .format(umac_name,office_id,time.time() - time_start))

    @staticmethod
    def get_ind_boards_be_upgraded(umac_name):
        logger.info("get ind boards to be upgraded")
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)

        # 查询独立单板信息
        ind_board_list = IndependentBoardManagement.get_ind_board_info(umac_dut)
        upgrade_ind_boards = IndependentBoardManagement.get_ind_boards_be_upgraded(ind_board_list,
                                                                                   umac_dut,
                                                                                   umac_config.src_ind_board_version_path)
        if not upgrade_ind_boards:
            logger.info("no ind boards need to be upgraded")
            return 0
        return len(upgrade_ind_boards)

    @staticmethod
    def delete_all_useless_versions_of_ind_boards(umac_name):
        logger.info("delete all useless versions of ind boards")
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        IndependentBoardManagement.delete_all_useless_versions_of_remote(umac_dut, upgrade_ind_boards)

    @staticmethod
    def delete_ind_board_files(umac_name):
        logger.info("delete ind board files")
        umac_config = uMacService.find_umac_config(umac_name)
        umac_omm = uMacService.find_umac_omm(umac_name)
        logger.info('delete subdirs and files below {0}'.format(umac_config.dst_ind_board_version_path))
        umac_omm.delete_dir(umac_config.dst_ind_board_version_path)

    @staticmethod
    def upgrade_ind_boards(umac_name):
        try:
            uMacService._upgrade_ind_boards(umac_name)
        except Exception,e:
            logger.warn("upgrade ind boards error:{0}".format(e))
        except:
            logger.warn("upgrade ind boards error")
    @staticmethod
    def _upgrade_ind_boards(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name)


        # 查询独立单板信息
        logger.info('upgrade ind boards:logout first and then login')
        umac_dut.logout()
        umac_dut.login_with_try(40)
        ind_board_list = IndependentBoardManagement.get_ind_board_info(umac_dut)
        upgrade_ind_boards = IndependentBoardManagement.get_ind_boards_be_upgraded(ind_board_list,
                                                                                   umac_dut,
                                                                                   umac_config.src_ind_board_version_path)
        # while len(upgrade_ind_boards) != 1:
        #     for board in upgrade_ind_boards:
        #         if board.id != '129':
        #             upgrade_ind_boards.remove(board)
        #             break
        # ind_board_list[
        #     0].version_file_name = r'D:\umac_ind_board_version\EGBS\EGBS_83XX_32_R_CE_V01.01.10.4.10_07300850.pkg'
        # upgrade_ind_boards = ind_board_list
        if not upgrade_ind_boards:
            logger.info("no ind boards need to upgrade")
            return
        # 删除无用的垃圾版本
        IndependentBoardManagement.delete_all_useless_versions_of_remote(umac_dut, upgrade_ind_boards)
        # 删除网管目标目录下的所有文件
        logger.info('delete subdirs and files below {0}'.format(umac_config.dst_ind_board_version_path))
        umac_omm.delete_dir(umac_config.dst_ind_board_version_path)
        # 上传各单板版本文件
        logger.info("upload ind version files to {0}".format(umac_config.dst_ind_board_version_path))
        dict_upload_ind_files = {}
        for ind_board in upgrade_ind_boards:
            dict_upload_ind_files[ind_board.version_file_name] = ""
        for upload_ind_file,_ in dict_upload_ind_files.items():
            upload_ind_file = upload_ind_file.replace('\\','/')
            umac_omm.upload_file_to_remote_dir(upload_ind_file, umac_config.dst_ind_board_version_path)

        # 加载各单板版本
        t1 = time.time()
        IndependentBoardManagement.create_thread_umac_dut(umac_config, upgrade_ind_boards)
        logger.info("start load ind board versions...")
        IndependentBoardManagement.load_ind_board_versions(umac_config, upgrade_ind_boards)
        logger.info("end load ind board versions:{0}".format(time.time() - t1))
        time.sleep(3*60)
        # 获取单板流水号
        logger.info("get version files serial no...")

        umac_dut.login_clean()
        IndependentBoardManagement.get_board_version_serial_nos(umac_dut, upgrade_ind_boards)

        # 获取omm 单板机架号，机框号

        umac_dut.login_clean()
        omm_boards_data = IndependentBoardManagement.get_omm_board_data(umac_dut)
        logger.info("omm boards(rack no, shelf no):{0}".format(omm_boards_data))

        # 默认激活
        logger.info("default active board versions...")

        umac_dut.login_clean()
        IndependentBoardManagement.default_active_board_versions(umac_dut, upgrade_ind_boards)

        # 生效单板
        logger.info("start valid boards...")
        umac_dut.login_clean()
        t = time.time()
        IndependentBoardManagement.valid_boards(umac_dut, upgrade_ind_boards, omm_boards_data)
        logger.info("end valid boards:{0}s".format(time.time() - t))
        # 释放资源
        IndependentBoardManagement.release_resource()

    @staticmethod
    def delete_useless_version_files(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)

        logger.info("start upgrade service version...")
        # 先清除历史垃圾文件
        ServiceVersionManagement.delete_useless_version_files(umac_dut)
        logger.info("delete useless service version files...")

    @staticmethod
    def delete_all_files_of_omm_server_dir(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_omm = uMacService.find_umac_omm(umac_name)
        logger.info("delete dir {0}...".format(umac_config.dst_service_version_path))
        umac_omm.delete_dir(umac_config.dst_service_version_path)

    @staticmethod
    def upload_version_files_to_omm_server_dir(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_omm = uMacService.find_umac_omm(umac_name)
        t1 = time.time()
        logger.info("upload version files from {0} to {1}".format(umac_config.src_service_version_path,
                                                                  umac_config.dst_service_version_path
                                                                  ))
        umac_omm.upload_service_version_files(umac_config.src_service_version_path,
                                              umac_config.dst_service_version_path)
        logger.info("end upload version files,{0}".format(time.time() - t1))

    @staticmethod
    def backup_zdb(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        t1 = time.time()
        logger.info("backup zdb...")
        ServiceVersionManagement.backup_zdb(umac_dut)
        logger.info("end backup zdb, {0}s".format(time.time() - t1))

    @staticmethod
    def upgrade_omm_zdb(umac_name):
        t1 = time.time()
        logger.info("upgrade omm zdb...")
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        ServiceVersionManagement.upgrade_zdb(umac_dut)
        logger.info("end upgrade omm zdb, {0}s".format(time.time() - t1))

    @staticmethod
    def load_and_active_version(umac_name):
        t1 = time.time()
        logger.info("load & active new versions...")
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        ServiceVersionManagement.load_and_active_version(umac_dut)
        logger.info("end load & active new versions, {0}s".format(time.time() - t1))

    @staticmethod
    def validate_version(umac_name):
        t1 = time.time()
        logger.info("enable versions...")
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        ServiceVersionManagement.validate_version(umac_dut)
        logger.info("end enabel vesions, {0}s".format(time.time() - t1))

    @staticmethod
    def syna(umac_name):
        t1 = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        logger.info("sleep {0}s before syna...".format(umac_config.syna_sleep_time))
        logger.info("syna...")
##        time.sleep(umac_config.syna_sleep_time)
#修改为判断状态后传表
        if uMacService.get_boardstatus_after_upgrade(umac_name):
            ServiceVersionManagement.syna(umac_dut)
        logger.info("end syna, {0}s".format(time.time() - t1))
        logger.info("end upgrade service version")

    @staticmethod
    def get_config_commands_and_save(umac_name,upgrade):
        upgrade = int(upgrade)
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name) #add by xjr 20160615
        umac_dut.login_clean()
        umac_config_command_html = ConfigCommandHtml(umac_dut, umac_config.rule_file)
        #执行前先清空本地目录
        local_path=umac_config.cmd_config_html_dir(upgrade).replace("/", "\\")
        umac_config.delete_allfiles(local_path)
        #增加查询网管内部版本的命令 add by xjr 20160615
        cmd='find /home/ngomm/'+umac_config.omm_url.split('/')[3]+'/server/conf/deploy-umac.properties -type f -name "deploy-umac.properties"  | xargs grep  "comm.app.version.main.id"'
        user_label=umac_omm.get_omm_interversion(cmd)
        spec_cmd='SHOW INNERWARESOFTMETERPARA:USERLABEL="'+user_label+'"'

        config_cmd_file = umac_config_command_html.get_config_commands_and_save(umac_config.cmd_config_html_dir(upgrade),spec_cmd)

        logger.info('umac config command to {0}'.format(config_cmd_file))
        return config_cmd_file

    @staticmethod
    def get_config_commands_html(umac_name, config_cmd_file,upgrade):
        logger.info('start get config command html')
        upgrade = int(upgrade)
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)

        html_file = IeCapture.generate_umac_config_command_html(umac_config, config_cmd_file,upgrade)
        logger.info('end get config command html, {0}s'.format(time.time() - t))
        return html_file
    #利用图形界面获取当前告警
    @staticmethod
    def get_alarm_file(umac_name, upgrade):
        logger.info('start get current alarm file')
        upgrade = int(upgrade)
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)

        save_path=umac_config.cmd_alarm_dir(upgrade).replace("/", "\\")
                #执行前先清空本地目录
        umac_config.delete_allfiles(save_path)
        if upgrade:
            save_path=save_path+'\\after_upgrade_current_alarm.csv'
        else:
            save_path=save_path+'\\before_upgrade_current_alarm.csv'
        IeCapture.get_alarm_file(umac_config,save_path)

        logger.info('end get current alarm file!, {0}s'.format(time.time() - t))

    #获取性能数据
    @staticmethod
    def get_performace_file(umac_name, upgrade):
        logger.info('start get current performance file')
        upgrade = int(upgrade)
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)

        save_path=umac_config.cmd_performance_dir(upgrade).replace("/", "\\")
                #执行前先清空本地目录
        umac_config.delete_allfiles(save_path)
        if upgrade:
            save_path=save_path+'\\after_upgrade_current_performance.csv'
        else:
            save_path=save_path+'\\before_upgrade_current_performance.csv'
        IeCapture.get_performance_file(umac_config,save_path)

        logger.info('end get current performace file!, {0}s'.format(time.time() - t))

#获取内存
    @staticmethod
    def get_memory_data(umac_name, upgrade):
        valid_board=[]
        logger.info('start get memory data')
        upgrade = int(upgrade)
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name)
        result=umacBoardstatusinfo.get_board_info(umac_dut)
        all_board=umacBoardstatusinfo.get_valid_board(result)
        #将升级前的正常态的信息写入文件
        if upgrade==0:
           board_path=umac_config.run_save_path
           board_path_file=board_path.replace("/", "\\")+'\\boardstatus.txt'
           board_file=open(board_path_file,'w')
           for i in range (0,len(all_board)):
                board_file.write(all_board[i]+'\n')
           board_file.close()


##        logger.info(all_board)
        moulde_type=umacBoardstatusinfo.get_moudle_type(umac_dut)
        unit_type=umacBoardstatusinfo.get_unit_type(umac_dut)
   ##        logger.info(moulde_type)
##        logger.info(unit_type)
        valid_board=umacBoardstatusinfo.get_collect_board(all_board,moulde_type,unit_type)
        memorydatapath=umac_config.cmd_memory_dir(upgrade).replace("/", "\\")
        umac_config.delete_allfiles(memorydatapath)
##        logger.info(memorydatapath)
        umac_omm.delete_dir('/autobackup')

        umac_omm.get_board_memory(valid_board)
        time.sleep(20)
        umac_omm.download_zdb_by_sftp(memorydatapath,'/autobackup')
        logger.info('end get memory data{0}s'.format(time.time() - t))

#获取升级后的单板状态，和升级前保存的对比，如果一致，则进行传表操作
    @staticmethod
    def get_boardstatus_after_upgrade(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        #读取升级前单板正常的信息
        boardstatus=False
        board_path=umac_config.run_save_path
        board_path_file=board_path.replace("/", "\\")+'\\boardstatus.txt'
        board_file=open(board_path_file,'r')
        boardlist=[]
        for line in board_file:
             line=line.rstrip('\n')
             boardlist.append(line)
        board_file.close()
##        logger.info(boardlist)
        boardlist.sort()
##        logger.info(boardlist)
        boardstatus=umacBoardstatusinfo.get_boardstatus(umac_dut,boardlist)
        return boardstatus






#保存前台zdb以及备份zip文件

    @staticmethod
    def get_backup_config_data(umac_name, upgrade):
        logger.info('start get backup config data')
        upgrade = int(upgrade)
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name)
##        umac_omm.delete_dir_files('/autobackup')
        umac_omm.delete_dir('/autobackup')
        cmd_configdata_path=umac_config.cmd_config_backupdata(upgrade).replace("/", "\\")
        logger.info('clear current files ')
        umac_config.delete_allfiles(cmd_configdata_path)
        #下载前台zdb文件
        logger.info('start download zdb files ')
        ServiceVersionManagement.backup_zdb(umac_dut)
        zdb_target_path=umac_config.omm_url.split("/")[3]
        zdb_target_path='/home/ngomm/'+ zdb_target_path +'/server/data/zdb/upgrade_onetime/'+ str(umac_config.office_id)
        umac_omm.download_zdb_by_sftp(cmd_configdata_path,zdb_target_path)
        #下载zip备份文件
        logger.info('start download zip files')
        ServiceVersionManagement.backup_configdata_mml(umac_dut)
        if upgrade:
           cmd_configdata_path=cmd_configdata_path +'\\after_upgrade_allcfg.zip'
        else:
           cmd_configdata_path=cmd_configdata_path +'\\before_upgrade_allcfg.zip'
        logger.info(cmd_configdata_path)
        umac_omm.download_file_by_sftp(cmd_configdata_path,'/autobackup/allcfg.zip')
        logger.info('end get backup config data!, {0}s'.format(time.time() - t))

   #获取反导命令
    @staticmethod
    def get_batchcommad_mml(umac_name):
        logger.info('start get batchcommand MMl')
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name)
        local_path=umac_config.run_save_path
        local_path_file=local_path.replace("/", "\\")+'\\Batchcommandmml.txt'
         #删除本地老文件
        if os.path.exists(local_path_file):
           os.remove(local_path_file)
        #采集前删除服务器上已存在的文件
        remote_path='/home/ngomm/'+umac_config.omm_url.split("/")[3]+'/server/tmp/exmml/txt'
        umac_omm.delete_dir_files(remote_path)
        #执行反导命令
        result_mml=umacBoardstatusinfo.run_get_commandmml(umac_dut)

        #获取导出结果文件
        if result_mml==-1:
          umac_omm.download_mml_file_by_ftp(local_path_file,remote_path)
        else :
          logger.info('This version does not support exp MML command')

        logger.info('end get batchcommand MMl!, {0}s'.format(time.time() - t))






    @staticmethod
    def get_output_path(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        return umac_config.output_dir

    @staticmethod
    def get_run_save_path(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        logger.info("run save path:{0}".format(umac_config.run_save_path))
        return umac_config.run_save_path

    @staticmethod
    def get_rule_file(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        return umac_config.rule_file
    #删除信令跟踪本地历史文件，执行前先删除本地已存在文件
    @staticmethod
    def  delete_sigtrace_file(umac_name,upgrade):
        upgrade = int(upgrade)

        umac_config = uMacService.find_umac_config(umac_name)
        sigtrace_path=umac_config.cmd_sigtrace_dir(upgrade).replace("/", "\\")

        umac_config.delete_allfiles(sigtrace_path)


    @staticmethod
    def compare_memory_alarm(umac_name):
        #比较内存
        logger.info("starting memory_comparision...")
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        before_path=umac_config.cmd_memory_dir(0).replace('/','\\')
        after_path=umac_config.cmd_memory_dir(1).replace('/','\\')
        outpath=umac_config.output_dir.replace('/','\\')
        ComparisionService.memeory_comparision(before_path,after_path,outpath)
        logger.info('end memory_comparision!, {0}s'.format(time.time() - t))
       #比较告警

        t = time.time()
        logger.info("Start alarm comparision...")
##        umac_config = uMacService.find_umac_config(umac_name)
        before_path=umac_config.cmd_alarm_dir(0).replace('/','\\')
        after_path=umac_config.cmd_alarm_dir(1).replace('/','\\')
        ComparisionService.alarm_comparision(before_path,after_path,outpath)
        logger.info('end alarm_comparision!, {0}s'.format(time.time() - t))
        #比较协议栈
        t = time.time()
        logger.info("Start ipstack comparision...")
##        umac_config = uMacService.find_umac_config(umac_name)
        before_path=umac_config.cmd_config_backupdata(0).replace('/','\\')+'\\ipstackall.txt'
        after_path=umac_config.cmd_config_backupdata(1).replace('/','\\')+'\\ipstackall.txt'
        ComparisionService.ipstack_txt_html(before_path,after_path,outpath)
        logger.info('end ipstack comparision!, {0}s'.format(time.time() - t))

       #比较性能任务
        t = time.time()
        logger.info('running')
##        print umac_config.cmd_performance_dir(0)
        before_path=umac_config.cmd_performance_dir(0).replace('/','\\')
        after_path=umac_config.cmd_performance_dir(1).replace('/','\\')
        logger.info(after_path)
        logger.info(before_path)
        outpath=umac_config.output_dir.replace('/','\\')
        logger.info(outpath)
        ComparisionService.performance_comparision(before_path,after_path,outpath)
        logger.info('end performance_comparision!, {0}s'.format(time.time() - t))





    @staticmethod
    def compare_html_config(umac_name):
        #比较Html配置差异
        logger.info("starting html_comparision...")
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        before_path=umac_config.cmd_config_html_dir(0).replace('/','\\')+'\\before_config_data.html'
        after_path=umac_config.cmd_config_html_dir(1).replace('/','\\')+'\\after_config_data.html'
        outpath=umac_config.output_dir.replace('/','\\')
        if not os.path.exists(before_path):
            logger.info("No html file of before upgrade")
            return
        if not os.path.exists(after_path):
            logger.info("No html file of after upgrade")
            return
        #对比前先清除当前目录下已经存在的文件
        # old_result_file=outpath +'\\summary.html'
        # if os.path.exists(old_result_file):
        #    os.remove(old_result_file)

        data=DataAnalysisService()

        #登陆数据平台
        data.combo_login('10022510','zte')
        #上传基准文件 上传比较文件
        data.compare_files_upload(base_path=before_path,new_path=after_path)

        #data.compare_files_upload()
        #选择分析规则
        data.select_rule(0,umac_config.rule_file)
         #根据规则比较文件
        result=data.compare()
        data.get_report(outpath,result)
        logger.info('end html_comparision!, {0}s'.format(time.time() - t))

#对比信令跟踪输出为html文件
    @staticmethod
    def compare_singinal_files(umac_name,difference=True):
        logger.info("starting singinal_comparision...")
        t = time.time()
        umac_config = uMacService.find_umac_config(umac_name)
        before_path=umac_config.cmd_sigtrace_dir(0).replace('/','\\')
        after_path=umac_config.cmd_sigtrace_dir(1).replace('/','\\')
        outpath=umac_config.output_dir.replace('/','\\')
        ComparisionService.compare_siginal(before_path,after_path,outpath,difference)
        logger.info('end singinal_comparision with html!, {0}s'.format(time.time() - t))

    @staticmethod
    def filter_by_config_cmd(umac_name,pstt_name):
        from testlib.service.EngineProxyService import EngineProxyService
        umac_config = uMacService.find_umac_config(umac_name)
        return EngineProxyService.filter_by_config_cmd_for_umac(pstt_name, umac_config)

    @staticmethod
    def umac_license_test(umac_name,path,by_index):
        i=0
        j=0
        by_index=int(by_index)
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name)
        neid=str(umac_config.office_id)
        if umac_config.office_id<250:
             logger.info(u'license验证请使用250及之后的局号')
             return

        #获取license文件，目前只支持一次处理一个，因此该目录下只能放一个license文件和对应的申请表
        for filename in os.listdir(path):
            if filename.endswith('.lic'):
                i+=1
            if filename.endswith('.xlsx') or filename.endswith('.xls') :
                j+=1
##        print j,i

        if i>1 or i==0 :
          logger.info(u'该目录下存在多个license文件或者没有license文件，请只放入当前要验证的文件')
          return
        if j>1 or j==0 :
          logger.info(u'该目录下存在多个license申请文件或者没有license申请文件，请只放入当前要验证的申请文件')
          return


        for filename in os.listdir(path):
            if filename.endswith('.lic'):
                lcsfile=os.path.join(path,filename)
                lcsfile_remote='/home/ngomm/'+umac_config.omm_url.split('/')[3]+'/server/conf/license/'+filename
            if filename.endswith('.xlsx') or filename.endswith('.xls') :
                apply_file=os.path.join(path,filename)


       #获取license申请表信息 add at 0530
        license_apply=[]
        license_info={}
        license_apply,license_info=umaclicensetest.get_license_appinfo(apply_file,by_index)
        if not license_info.has_key('Netype') or not license_info.has_key('Version') :
             logger.info(u'申请表中没有网元信息或者版本信息，请确认补充正确后继续')
             return

     #获取网管服务器上的对应局的版本信息，由于不知道实际已经安装的类型，只能三种都检查 add at 0530
        logger.info(u'获取服务器版本信息')
        omm_version={}
        combo_cmd='find /home/ngomm/combo_mmegngp_sgsn_'+neid+'/client/pub/main/ -type f -name "main-frame-config.xml"  | xargs grep  "verShow"'
        sgsn_cmd='find /home/ngomm/gngp_sgsn_'+neid+'/client/pub/main/ -type f -name "main-frame-config.xml"  | xargs grep  "verShow"'
        mme_cmd='find /home/ngomm/mme_'+neid+'/client/pub/main/ -type f -name "main-frame-config.xml"  | xargs grep  "verShow"'
##        logger.info(combo_cmd)
        omm_combo=umac_omm._get_omm_version_no(combo_cmd)
        logger.info(omm_combo)
        if len(omm_combo)>0:
           omm_version['Combo MME/GnGp SGSN']=omm_combo
        omm_sgsn=umac_omm._get_omm_version_no(sgsn_cmd)
        logger.info(omm_sgsn)
        if len(omm_sgsn)>0:
           omm_version['GnGp SGSN']=omm_sgsn
        omm_mme=umac_omm._get_omm_version_no(mme_cmd)
        logger.info(omm_mme)
        if len(omm_mme)>0:
           omm_version['MME']=omm_mme
##        for k,v in omm_version.items():
##            logger.info(k+'333333333:'+v)

     #先判断申请表中的网元类型是否和现在安装的一致
        app_versioninfo=re.findall('(\V\d\.\d+.\d+\.\w*\d*\.*\w*\d*)',license_info['Version'])
##        logger.info(app_versioninfo[0])
        app_version=app_versioninfo[0][:8]
        logger.info(app_version)
        versionfile=''
        logger.info(license_info['Netype'].strip())
        if not omm_version.has_key(license_info['Netype'].strip()) :
            #直接 删除当前网元，重新安装版本后验证
            logger.info(u'当前局和申请表中的局类型不一致，将重新安装后验证')
            for filename in os.listdir(path):
##               logger.info(app_versioninfo[0])
##               logger.info(filename)
               if filename.find(app_versioninfo[0])!=-1 and filename.endswith('.tar.gz'):
##                  logger.info(filename)
                  versionfile=os.path.join(path,filename)
                  break
##               else :
##                  logger.info(u'请将license申请对应的OMM版本拷贝到'+path)
##                  return
            if len(versionfile)>0 :
             uMacService.reinstall_omm(umac_omm,neid,versionfile,license_info['Netype'].strip())
            else:
                logger.info(u'License所在目录无对应的网管版本，请先拷贝到目标网管版本至该目录下')
                return

        else :

            cur_ver=omm_version[license_info['Netype'].strip()][:8]
            logger.info(cur_ver)
            logger.info(app_version)
            if app_version!=cur_ver :
             #直接 删除当前网元，重新安装版本后验证
              logger.info(u'当前局和申请表中的版本不一致，将重新安装后验证')
              for filename in os.listdir(path):
               if filename.find(app_versioninfo[0])!=-1 and filename.endswith('.tar.gz'):
                  versionfile=os.path.join(path,filename)
                  break

              if len(versionfile)>0 :
                 uMacService.reinstall_omm(umac_omm,neid,versionfile,license_info['Netype'].strip())
              else :
                logger.info(u'License所在目录无对应的网管版本，请先拷贝到目标网管版本至该目录下')
                return
        if license_info['Netype'].strip()=='GnGp SGSN':
            netypeid='gngp_sgsn_'+neid
        if license_info['Netype'].strip()=='MME':
            netypeid='mme_'+neid
        if license_info['Netype'].strip()=='Combo MME/GnGp SGSN':
            netypeid='combo_mmegngp_sgsn_'+neid


        for filename in os.listdir(path):
            if filename.endswith('.lic'):
                lcsfile=os.path.join(path,filename)
                lcsfile_remote='/home/ngomm/'+netypeid+'/server/conf/license/'+filename
        #上传license文件
        umac_omm.upload_file_by_sftp(lcsfile,lcsfile_remote)
        umac_dut.logout()
        umac_dut.login_with_try(10)

        #验证license
        umaclicensetest.compare_license_info(umac_dut,license_apply,license_info)

    @staticmethod
    def reinstall_omm(umac_omm,officeid,versionfile,netype):
##        for filename in os.listdir(path):
##            if filename.find(version)!=-1:
##                  versionfile=os.path.join(path,filename)
##            else :
##                  logger.info(u'请将license申请对应的OMM版本拷贝到'+path)
##                  return

        umac_omm._delete_cur_omm(officeid)
        umac_omm.delete_dir('/home/version/omm')
        umac_omm.upload_file_to_remote_dir(versionfile,'/home/version/omm')
        umac_omm._install_new_omm('/home/version/omm',officeid,netype)
        time.sleep(45) #等待30s后加载激活license





    @staticmethod
    def omp_poweroff(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        #下电前检查信令跟踪文件是否已经存在
        sigpath=umac_config.cmd_sigtrace_dir(0)

        if not umac_config.check_files(sigpath):
            raise Exception(u' 升级前信令跟踪文件没有保存成功，终止升级！请检查'+sigpath)

        omp_status={}
        omp_status=umacBoardstatusinfo.get_ecmm_omp_boardinfo(umac_dut)
##        for k,v in omp_status.iteritems():
##            logger.info(k+':'+v)
##        if omp_status.has_key('M') and omp_status.has_key('S'):
##            logger.info(omp_status['M'])
        logger.info(u' 开始下电备用OMP！')
        umacBoardstatusinfo.get_omp_poweroff(umac_dut,omp_status)
        time.sleep(30)
        logger.info(u' 备用OMP下电完成！')
##        else:
##             logger.info(u' 当前局无备用OMP，无法下电！')


    @staticmethod
    def omp_poweron_swp(umac_name):
        result=0
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        omp_status={}
        omp_status=umacBoardstatusinfo.get_ecmm_omp_boardinfo(umac_dut)
        #上电前先检查主用OMP的版本是否是目标版本，如果不是则终止后续流程
        omp_localver=umac_config.ser_version_no.lower()
        omp_localver=omp_localver.replace('v','')
        #获取前台版本
        omp_frever=umacBoardstatusinfo.get_omp_ver(umac_dut,omp_status)
        logger.info(u'升级后版本：'+omp_frever+u'目标版本：'+omp_localver)
        if omp_localver!=omp_frever:
            raise Exception(u'升级后的业务版本和目标版本不一致，升级流程终止！')

        logger.info(u'等待备用OMP上电！')
        result=umacBoardstatusinfo.get_omp_poweron(umac_dut,omp_status)
        if result==-1:
           time.sleep(15)
           if umacBoardstatusinfo.get_omp_st(umac_dut,omp_status):
             logger.info(u'备用OMP上电完成，等待备用OMP倒换')
             time.sleep(310)
             umacBoardstatusinfo.get_omp_swp(umac_dut,omp_status)
##             time.sleep(10)

        else:
             logger.info(u' 当前局无备用OMP，无法上电！')

    @staticmethod
    def get_ipstackall(umac_name,upgrade):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        logger.info(u' 开始获取协议栈配置')
        umac_dut.login_clean()
        result=umacBoardstatusinfo.get_ipstackall(umac_dut)
        upgrade=int(upgrade)
        ipfilepath=umac_config.cmd_config_backupdata(upgrade).replace("/", "\\")+'\\ipstackall.txt'

        #将协议栈数据写入文件

        ipfile=open(ipfilepath,'w')
        ipfile.write(result)
        ipfile.close()
        logger.info(u' 结束获取协议栈配置')

    @staticmethod
    def get_license(umac_name,upgrade):
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        logger.info(u' start get license')
        upgrade = int(upgrade)
        uMacLicense().get_and_save_license(umac_dut,umac_config.cmd_license_dir(upgrade))
        logger.info(u' save license to {0}'.format(umac_config.cmd_license_dir(upgrade)))
        uMacService._get_ne_geration(umac_config,umac_dut)

    @staticmethod
    def _get_ne_geration(umac_config, umac_dut):
        logger.info(u' start get ne generation')
        ne_generation = NeGeneration(umac_dut)
        _2g, _3g, _4g = ne_generation.get_result()
        umac_config.set_ne_generation(_2g,_3g,_4g)
        logger.info(u' end get ne generation:2g = {0}, 3g = {0}, 4g = {0}'.format(_2g,_3g,_4g))

    # @staticmethod
    # def generate_function_stutas_excel(rule_file, html_file):
    #     return FunctionAnalysis.analysis_function(rule_file, html_file)

    @staticmethod
    def update_function_charactor(umac_name):
        from testlib.domain.umac.umacfunctioncharactorrefresh import refresh_function_charactor
        logger.info(u' start update function charactor')
        umac_config = uMacService.find_umac_config(umac_name)
        refresh_function_charactor(umac_config)
        logger.info(u' end update function charactor')


    @staticmethod
    def update_license_file(umac_name):

        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        umac_omm = uMacService.find_umac_omm(umac_name)
        netypeid=umac_config.netypeid
        lice_path=umac_config.local_save_path
        lce_upgrad=umac_config.lice_upgrade
        lcsfile=''
        lcsfile_remote=''
        if lce_upgrad=='y':
            for filename in os.listdir(lice_path):
                if filename.endswith('.lic'):
                    lcsfile=os.path.join(lice_path,filename)
                    lcsfile_remote='/home/ngomm/'+netypeid+'/server/conf/license/'+filename
                    break

            #上传license文件
            del_cmd='rm -rf /home/ngomm/'+netypeid+'/server/conf/license/*.lic'
            umac_omm._ssh.exec_command(del_cmd)
            time.sleep(3)
            umac_omm.upload_file_by_sftp(lcsfile,lcsfile_remote)
            umac_dut.logout()
            umac_dut.login_with_try(10)
            umaclicensetest.run_active_license(umac_dut)
            logger.info(u' 更换license完成！')
        else:
            logger.info(u' No need upgrade license file')
    @staticmethod
    def test_xjr(umac_name):
        omm = uMacService.find_umac_omm(umac_name)
        umac_config = uMacService.find_umac_config(umac_name)
        vercmd='find /home/ngomm/'+umac_config.omm_url.split('/')[3]+'/client/pub/main/ -type f -name "main-frame-config.xml"  | xargs grep  "verShow"'
        ommupd_version=omm._get_omm_version_no(vercmd)
        logger.info(ommupd_version)



    @staticmethod
    def get_alarm_data(umac_name, upgrade):
        upgrade=int(upgrade)
        umac_config = uMacService.find_umac_config(umac_name)
        umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        before_path=umac_config.cmd_alarm_dir(0).replace("/", "\\")
        after_path=umac_config.cmd_alarm_dir(1).replace("/", "\\")   
        
        save_path1=before_path+'\\before_upgrade_current_alarm.xlsx'
        #umac_config.delete_allfiles(save_path1)
        save_path2=after_path+'\\after_upgrade_current_alarm.xlsx'
       
        # save_path = umac_config.output_dir+'\\alarm_comparision.xlsx'
        # save_path = umac_config.output_dir + '\\upgrade_report.html'
        if upgrade:
            if os.path.exists(save_path2):
                os.remove(save_path2)
            # umac_config.delete_allfiles(after_path)
            # if os.path.exists(save_path):
            #     os.remove(save_path)
            GetAlarmData.get_alarm_data(umac_dut, save_path2)
            # save_path1 = umac_config.cmd_alarm_dir(0).replace("/", "\\") +'\\before_upgrade_current_alarm.xlsx'
            # GetAlarmData.alarm_compare(save_path, before_path, after_path, save_path1, save_path2)
            
        else:
            if os.path.exists(save_path1):
                os.remove(save_path1)
            # umac_config.delete_allfiles(before_path)
            GetAlarmData.get_alarm_data(umac_dut, save_path1)

    @staticmethod
    def get_performance_task(umac_name, upgrade):
        upgrade=int(upgrade)
        umac_config = uMacService.find_umac_config(umac_name)
        omm = uMacService.find_umac_omm(umac_name)
        before_path = umac_config.cmd_performance_dir(0).replace("/", "\\")
        after_path = umac_config.cmd_performance_dir(1).replace("/", "\\")
        
        # save_path = umac_config.output_dir + '\\upgrade_report.html'
        save_path1=before_path+'\\before_upgrade_current_performance.xlsx'
        save_path2=after_path+'\\after_upgrade_current_performance.xlsx'
        
        #下载性能任务的db文件
        local_path = umac_config.run_save_path+'\\sqlite_pm_tm.db'
        if os.path.exists(local_path):
            os.remove(local_path)
        remote_path = r'/home/ngomm_data/ngomm_db/{0}/sqlite_pm_tm.db'.format(umac_config.omm_url.split("/")[3])
        omm.download_file_by_sftp(local_path, remote_path)

        if upgrade:
            if os.path.exists(save_path2):
                os.remove(save_path2)
            # umac_config.delete_allfiles(after_path)
            get_pm_task.WriteInExcel(local_path, save_path2)
            # get_pm_task.pmtask_compare(save_path, before_path, after_path, save_path1, save_path2)

        else:
            if os.path.exists(save_path1):
                os.remove(save_path1)
            # umac_config.delete_allfiles(before_path)
            get_pm_task.WriteInExcel(local_path, save_path1)


    @staticmethod
    def all_compare(umac_name):
        #告警
        # upgrade=int(upgrade)
        umac_config = uMacService.find_umac_config(umac_name)
        # umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
        before_path=umac_config.cmd_alarm_dir(0).replace("/", "\\")
        after_path=umac_config.cmd_alarm_dir(1).replace("/", "\\")
        
        save_path1=before_path+'\\before_upgrade_current_alarm.xlsx'
        #umac_config.delete_allfiles(save_path1)
        save_path2=after_path+'\\after_upgrade_current_alarm.xlsx'
        
        # save_path = umac_config.output_dir+'\\alarm_comparision.xlsx'
        save_path = umac_config.output_dir + '\\upgrade_report.html'
        logger.info(save_path)
        if os.path.exists(save_path):
            os.remove(save_path)
        # if upgrade:
        #     umac_config.delete_allfiles(after_path)
        #     if os.path.exists(save_path):
        #         os.remove(save_path)
        #     GetAlarmData.get_alarm_data(umac_dut, save_path2)
            # save_path1 = umac_config.cmd_alarm_dir(0).replace("/", "\\") +'\\before_upgrade_current_alarm.xlsx'
        
        logger.info('对比告警')
        GetAlarmData.alarm_compare(save_path, before_path, after_path, save_path1, save_path2)
            
        # else:
        #     umac_config.delete_allfiles(before_path)
        #     GetAlarmData.get_alarm_data(umac_dut, save_path1)




        #性能任务
        # omm = uMacService.find_umac_omm(umac_name)
        logger.info('对比性能')
        before_path = umac_config.cmd_performance_dir(0).replace("/", "\\")
        after_path = umac_config.cmd_performance_dir(1).replace("/", "\\")
        
        
        save_path1=before_path+'\\before_upgrade_current_performance.xlsx'
        save_path2=after_path+'\\after_upgrade_current_performance.xlsx'
        #下载性能任务的db文件
        # local_path = umac_config.run_save_path+'\\sqlite_pm_tm.db'
        # remote_path = r'/home/ngomm_data/ngomm_db/{0}/sqlite_pm_tm.db'.format(umac_config.omm_url.split("/")[3])
        # omm.download_file_by_sftp(local_path, remote_path)

        # if upgrade:
        #     umac_config.delete_allfiles(after_path)
        #     get_pm_task.WriteInExcel(local_path, save_path2)
        get_pm_task.pmtask_compare(save_path, before_path, after_path, save_path1, save_path2)

        # else:
        #     umac_config.delete_allfiles(before_path)
        #     get_pm_task.WriteInExcel(local_path, save_path1)


        #内存
        logger.info('对比内存')
        before_path=umac_config.cmd_memory_dir(0).replace('/','\\')
        # print before_path
        after_path=umac_config.cmd_memory_dir(1).replace('/','\\')
        # print after_path
        # if upgrade:
        #     umac_config.delete_allfiles(after_path)
        #     uMacService.get_memory_data(umac_name, 1)
        ComparisionService.memeory_comparision(before_path,after_path,save_path)
        # else:
        #     umac_config.delete_allfiles(before_path)
        #     uMacService.get_memory_data(umac_name, 0)



        #协议栈
        logger.info('对比协议栈')
        before_path=umac_config.cmd_config_backupdata(0).replace('/','\\')
        save_path1=before_path+'\\ipstackall.txt'
        after_path=umac_config.cmd_config_backupdata(1).replace('/','\\')
        save_path2=after_path+'\\ipstackall.txt'
        # if upgrade:
        #     if os.path.exists(save_path2):
        #         os.remove(save_path2)
        #     uMacService.get_ipstackall(umac_name,1)
        ComparisionService.compare_ipstack(umac_config, save_path1,save_path2,save_path)
        # else:
        #     if os.path.exists(save_path1):
        #         os.remove(save_path1)
        #     uMacService.get_ipstackall(umac_name,0)

        




    # @staticmethod
    # def test_dww_2(umac_name, upgrade):
    #     upgrade = int(upgrade)
    #     omm = uMacService.find_umac_omm(umac_name)
    #     umac_config = uMacService.find_umac_config(umac_name)
    #     umac_dut = uMacService.find_umac_dut(umac_name, umac_config.office_id)
    #     save_path=umac_config.cmd_performance_dir(upgrade).replace("/", "\\")
    #     save_path2=save_path+'\\after_upgrade_current_performance.xlsx'
    #     save_path1=save_path+'\\before_upgrade_current_performance.xlsx'
    #     umac_config.delete_allfiles(save_path)
    #     #下载性能任务的db文件
    #     local_path = umac_config.run_save_path+'\\sqlite_pm_tm.db'
    #     save_path = umac_config.output_dir+'\\all_comparison.html'
    #     remote_path = r'/home/ngomm_data/ngomm_db/{0}/sqlite_pm_tm.db'.format(umac_config.omm_url.split("/")[3])
    #     omm.download_file_by_sftp(local_path, remote_path)
    #     if upgrade:
    #         get_pm_task.WriteInExcel(local_path, save_path2)
    #         save_path1=umac_config.cmd_performance_dir(0).replace("/", "\\")+'\\before_upgrade_current_performance.xlsx'
    #         get_pm_task.Compare(save_path, save_path1, save_path2)

    #     else:
    #         get_pm_task.WriteInExcel(local_path, save_path1)

    # @staticmethod
    # def test_dww_3(umac_name):
        #比较内存
        # uMacService.get_memory_data(umac_name, 0)
        # uMacService.get_memory_data(umac_name, 1)
        # logger.info("starting memory_comparision...")
        # t = time.time()
        # umac_config = uMacService.find_umac_config(umac_name)
        # before_path=umac_config.cmd_memory_dir(0).replace('/','\\')
        # after_path=umac_config.cmd_memory_dir(1).replace('/','\\')
        # outpath=umac_config.output_dir.replace('/','\\')+'\\all_comparison.html'
        # ComparisionService.memeory_comparision(before_path,after_path,outpath)
        # logger.info('end memory_comparision!, {0}s'.format(time.time() - t))
        

        #比较协议栈
        # uMacService.get_ipstackall(umac_name,0)
        # uMacService.get_ipstackall(umac_name,1)
        # t = time.time()
        # logger.info("Start ipstack comparision...")
        # umac_config = uMacService.find_umac_config(umac_name)
        # before_path=umac_config.cmd_config_backupdata(0).replace('/','\\')+'\\ipstackall.txt'
        # after_path=umac_config.cmd_config_backupdata(1).replace('/','\\')+'\\ipstackall.txt'
        # outpath=umac_config.output_dir.replace('/','\\')+'\\summary.html'
        # ComparisionService.compare_ipstack(before_path,after_path,outpath)
        # logger.info('end ipstack comparision!, {0}s'.format(time.time() - t))

        # uMacService.compare_singinal_files(umac_name,difference=True)


            
        

if __name__ == '__main__':
    # uMacService.generate_function_stutas_excel(ur'D:\project_version_valid\prepare\合并英文规则表-去除不支持部分.xlsx',
    #                                            ur'D:\project_version_valid\prepare\1510B28a4.html')
    # uMacService.upgrade_omm("195.137.81.55",
    #                         "root",
    #                         "klinux1",
    #                         "admin",
    #                         "",
    #                         "7722",
    #                         "29")
    # uMacService.init_umac('aaa', [1, 2, 3])
    IeCapture.generate_umac_config_command_html()
