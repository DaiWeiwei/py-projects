# coding:utf-8
import os
import time
from subprocess import Popen
from robot.api import logger
import win32gui
import win32con
from testlib.infrastructure.device.engineproxy.EngineProxyCreator import EngineProxyCreator
from testlib.domain.ne.simu_ne.SimuPstt import SimuPstt
from testlib.domain.ne.NeRepository import NeRepository
from testlib.infrastructure.utility.wmi import WMI


class EngineProxyService(object):
    g_pstt_ip = ""
    g_pstt_port = ""
    g_pstt_name = ""
    g_run_save_path = ""
    g_pstt_path = ""
    g_pstt_open_wait_time = 60
    g_pstt_name = 'pstt'
    g_pstt_signal_trace_flag = 0
    @staticmethod
    def init_pstt(pstt_ip, pstt_port, pstt_name, run_save_path):
        run_save_path = run_save_path.strip()
        if not run_save_path:
            raise Exception("run save path is empty, please check config first!")
        logger.info("create_pstt_proxy:ip = {0}, port = {1}, alias = {2}".format(pstt_ip, pstt_port, pstt_name))
        proxy = EngineProxyCreator.create_engine_proxy(pstt_ip, pstt_port, pstt_name)
        simu_pstt = SimuPstt(pstt_name, pstt_ip, pstt_name)
        simu_pstt.engine = proxy
        NeRepository().add(pstt_name, simu_pstt)
        simu_pstt.send_config_to_pstt({"run_save_path":run_save_path})
        EngineProxyService.g_pstt_ip = pstt_ip
        EngineProxyService.g_pstt_port = pstt_port
        EngineProxyService.g_pstt_name = pstt_name
        EngineProxyService.g_run_save_path = run_save_path
        EngineProxyService.g_pstt_name = pstt_name

    @staticmethod
    def release_pstt(pstt_name):
        EngineProxyCreator.delete_engine_proxy(pstt_name)
        logger.info("release_pstt:{0}".format(pstt_name))
        # simu_pstt = EngineProxyService.find_simu_ne(pstt_name)

    @staticmethod
    def find_simu_ne(alias):
        return NeRepository().find(alias)

    @staticmethod
    def open_pstt(pstt_path, wait_time=30):
        if not os.path.isfile(pstt_path):
            raise Exception("pstt_path:{0}, is not a file".format(pstt_path))
        EngineProxyService.g_pstt_path = pstt_path
        EngineProxyService.g_pstt_open_wait_time = wait_time
        logger.info("start openpstt...")
        Popen(pstt_path)
        time.sleep(wait_time)
        logger.info("end open pstt")
    @staticmethod
    def close_pstt():
        NeRepository().clear()
        EngineProxyCreator.delete_engine_proxy(EngineProxyService.g_pstt_name)
        logger.info("close pstt...")
        os.system("taskkill /F /IM pstt.exe /T")
        time.sleep(5)

    @staticmethod
    def check_pstt_open():
        wmi = WMI()
        for p in wmi.Win32_Process(name="PSTT.exe"):
            return True
        return False
    @staticmethod
    def predeal_for_run_pstt():
        if not EngineProxyService.check_pstt_open():
            logger.info("pstt is close,please wait for minutes...")
            EngineProxyService.open_pstt(EngineProxyService.g_pstt_path,EngineProxyService.g_pstt_open_wait_time)
            EngineProxyService.init_pstt(EngineProxyService.g_pstt_ip,
                                         EngineProxyService.g_pstt_port,
                                         EngineProxyService.g_pstt_name,
                                         EngineProxyService.g_run_save_path)
    @staticmethod
    def run_pstt(pstt_name,upgrade=0,select_last_run_cases=0):
        logger.info("start check pstt is open...")
        EngineProxyService.predeal_for_run_pstt()
        upgrade = int(upgrade)
        select_last_run_cases = int(select_last_run_cases)
        logger.info("start run pstt:{0},upgrade={1}...".format(pstt_name,upgrade))
        simu_pstt = EngineProxyService.find_simu_ne(pstt_name)

        #send config
        simu_pstt.send_sigtrace_flag(EngineProxyService.g_pstt_signal_trace_flag)

        simu_pstt.send_run_pstt(upgrade,select_last_run_cases)
        return simu_pstt.is_run_with_all_success()

    @staticmethod
    def filter_pstt_by_show_running_config(pstt_name, show_running_analysis_result_file,soft_para_file):
        logger.info("filter pstt by show running config: pstt_name = {0}, show running analysis result file = {1},soft para file={2}".format(pstt_name, show_running_analysis_result_file, soft_para_file))
        simu_pstt = EngineProxyService.find_simu_ne(pstt_name)
        return simu_pstt.send_filter_pstt_project_by_apn_config(show_running_analysis_result_file,soft_para_file)


    @staticmethod
    def classify_show_running_config_by_cases(pstt_name, show_running_analysis_result_file,soft_para_file):
        logger.info("classify show running config by cases: pstt_name = {0}, show running analysis file = {1}, soft para file ={2}".format(pstt_name, show_running_analysis_result_file,soft_para_file))
        simu_pstt = EngineProxyService.find_simu_ne(pstt_name)
        return simu_pstt.send_classify_show_running_config_by_cases(show_running_analysis_result_file,soft_para_file)

    @staticmethod
    def upgrade_fore_version(run_result, update_strategy):
        update_strategy = int(update_strategy)
        if update_strategy == 0:
            logger.info(u'策略设置，不升级前台版本')
            return
        ##用例执行失败，则不升级
        elif update_strategy == 1 and not run_result:
            raise Exception(u'用例执行失败,不升级前台')
            return
        logger.info(u'开始升级前台...')

    @staticmethod
    def set_sigtrace_flag(pstt_name, flag):
        flag = not not flag
        EngineProxyService.g_pstt_signal_trace_flag = flag
        logger.info("set sigtrace flag = {0}".format(flag))
        #simu_pstt = EngineProxyService.find_simu_ne(pstt_name)
        #simu_pstt.send_sigtrace_flag(flag)
    @staticmethod
    def set_pstt_strategy(pstt_name, match_no_mml_case,run_mml):
        logger.info("set filter strategy: match_no_mml_case = {0},run_mml = {1} to {2}".format(match_no_mml_case, run_mml, pstt_name))
        simu_pstt = EngineProxyService.find_simu_ne(pstt_name)
        simu_pstt.match_no_mml_case = int(match_no_mml_case)
        simu_pstt.run_mml = int(run_mml)
    @staticmethod
    def notify_upgrade_state(pstt_name = 'pstt',upgraded = False):
        logger.info("notify upgrade [{0}] to {1}".format(upgraded, pstt_name))
        simu_pstt = EngineProxyService.find_simu_ne(pstt_name)
        simu_pstt.fore_version_upgrade = upgraded

    @staticmethod
    def filter_by_config_cmd_for_umac(pstt_name,umac_config):
        logger.info("filter by config cmd for umac:pstt_name = {0}".format(pstt_name))
        simu_pstt = EngineProxyService.find_simu_ne(pstt_name)
        return simu_pstt.send_filter_by_config_cmd_for_umac(umac_config)


if __name__ == '__main__':
    # EngineProxyService.create_pstt_proxy("","","aa")
    # EngineProxyService.open_pstt(r'E:\linxing\B15\Output\Debug\pstt.exe')
    pstt_name = "pstt"
    #EngineProxyService.init_pstt("10.42.188.33", 50200, pstt_name,'c:')
    # EngineProxyService.set_pstt_procedure_path(pstt_name,"d:")
    # EngineProxyService.filter_pstt(pstt_name, [u"apn",u"apn2"])
    # EngineProxyService.run_pstt(pstt_name)
    # EngineProxyService.run_pstt(pstt_name)
    # wmi = WMI()
    # for p in wmi.Win32_Process(name="PSTT.EXE"):
    #    print '111111111'
