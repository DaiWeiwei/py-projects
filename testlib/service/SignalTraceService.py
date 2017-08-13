# coding:utf-8
import time
import os
import shutil
import subprocess
import sys
from multiprocessing import Process,Pool
from testlib.infrastructure.iecapture.iecapture import IeCapture
from testlib.service.uMacService import uMacService
from testlib.service.XgwService import XgwService
from robot.api import logger
from testlib.infrastructure.foreigntool.sigtracecomparison import SigalTraceComparison

# reload(sys)
# sys.setdefaultencoding('utf8')

class SignalTraceService(object):
    @staticmethod
    def xgw_change_zdat_to_txt(xgw_name):
        xgw_config = XgwService.find_xgw_config(xgw_name)
        if not xgw_config:
            raise Exception("cannot find xgw config of {0}".format(xgw_name))
        t1 = time.time()
        logger.info("start change zdat to txt ...")
        SignalTraceService.change_zdat_to_txt_for_xgw(xgw_config.host,
                                              xgw_config.telnet_user_name,
                                              xgw_config.telnet_password,
                                              '{0}[]{1}'.format(xgw_config.sigtrace_path_0,
                                                                xgw_config.sigtrace_path_1),
                                              xgw_config.is_en)

        logger.info("end change zdat to txt, {0}ms", time.time() - t1)

    @staticmethod
    def umac_change_zdat_to_txt(umac_name):
        umac_config = uMacService.find_umac_config(umac_name)
        if not umac_config:
            raise Exception("cannot find umac config of {0}".format(umac_name))
        sigpath=umac_config.cmd_sigtrace_dir(1)
        if not umac_config.check_files(sigpath):
            raise Exception(u' 升级后信令跟踪文件没有保存成功，终止信令跟踪比较！')
        signal_wash_path_0 = os.path.join(umac_config.sigtrace_path_0, 'after_wash')
        try : 
            shutil.rmtree(signal_wash_path_0)
        except:
            pass
        finally:
            os.mkdir(signal_wash_path_0)
        signal_wash_path_1 = os.path.join(umac_config.sigtrace_path_1, 'after_wash')
        try : 
            shutil.rmtree(signal_wash_path_1)
        except:
            pass
        finally:
            os.mkdir(signal_wash_path_1)
        
        t1 = time.time()
        logger.info("start change zdat to txt ...")
##        SignalTraceService.change_zdat_to_txt_for_umac(umac_config.omm_url,
##                                              umac_config.telnet_user_name,
##                                              umac_config.telnet_password,
##                                              '{0}[]{1}'.format(umac_config.sigtrace_path_0,
##                                                                umac_config.sigtrace_path_1),
##                                              umac_config.is_en)
        # SignalTraceService.change_zdat_to_txt_by_officeline_for_umac(umac_config.sigtrace_path_0)
        time.sleep(5)
        SignalTraceService.signal_wash(signal_wash_path_0, umac_config.sigtrace_path_0)
        # SignalTraceService.change_zdat_to_txt_by_officeline_for_umac(umac_config.sigtrace_path_1)
        SignalTraceService.signal_wash(signal_wash_path_1, umac_config.sigtrace_path_1)
      
    @staticmethod
    def umac_signal_trace_comparision(umac_name, just_compare_send):
        umac_config = uMacService.find_umac_config(umac_name)
        if not umac_config:
            raise Exception("cannot find umac config of {0}".format(umac_name))
        # return SignalTraceService.signal_trace_comparision(umac_config.sigtrace_path_0,
        #                                                    umac_config.sigtrace_path_1,
        #                                                    umac_config.output_dir
        #                                                    )
        SignalTraceService.create_bat(SignalTraceService.init_dir(umac_config),just_compare_send)

    @staticmethod
    def create_bat(path_list,just_compare_send):
        bat_name = r'run.bat'
        bat_path = os.path.split(os.path.dirname(__file__))[0] + '\\domain\\umac'
        # print bat_path
        bat_file_path = os.path.join(bat_path,bat_name)
        with open(bat_file_path, 'w') as f: 
            # f.write('C:' + '\n')         
            f.write(r'cd {0}'.format(bat_path) + '\n')
            f.write(r'{0}:'.format(bat_path.split(':')[0]) + '\n')
            f.write(r'python sig_compare.py {0} {1} {2}'.format(path_list[0],path_list[1],just_compare_send))
        # os.system(bat_file_path)
        # cmdline="{0}".format(bat_name) 
        # cmdline="run.bat {0} {1} {2} {3} {4}".format(path_list[0],path_list[1],path_list[2],path_list[3],path_list[4]) 
        try:
            ps = subprocess.Popen(bat_name,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell = True,
                                  cwd =bat_path)#creationflags=0x08)#)
            (stdout, stderr) = ps.communicate()
            print stdout
            print stderr
        except Exception,e:           
            return None, None
        # os.remove(bat_file_path)
    
    @staticmethod
    def init_dir(umac_config):
        # before_dir = os.path.join(umac_config.sigtrace_path_0, 'after_wash')     
        # after_dir = os.path.join(umac_config.sigtrace_path_1, 'after_wash')
        premitive_file_dir = umac_config.output_dir.replace('/','\\')+'\\compared_sigtrace'
        try:
            shutil.rmtree(premitive_file_dir)
        except:
            pass
        finally:
            os.mkdir(premitive_file_dir)
        
        compared_file = umac_config.output_dir.replace('/','\\')+'\\sig_comparison.html'
        if os.path.exists(compared_file):
            os.remove(compared_file)
        
        xml_dir = os.path.split(os.path.dirname(__file__))[0] + '\\filters'
        if not os.path.exists(xml_dir) or not os.listdir(xml_dir):
            raise Exception('XML files are not raady.!')
        return umac_config.run_save_path.replace('/','\\'),xml_dir
    
    @staticmethod
    def xgw_signal_trace_comparision(xgw_name):
        xgw_config = XgwService.find_xgw_config(xgw_name)
        if not xgw_config:
            raise Exception("cannot find xgw config of {0}".format(xgw_name))
        return SignalTraceService.signal_trace_comparision(xgw_config.sigtrace_path_0,
                                                           xgw_config.sigtrace_path_1,
                                                           xgw_config.output_dir
                                                           )
    @staticmethod
    def change_zdat_to_txt_for_umac(omm_url, telnet_user_name, telnet_password, signal_trace_path_list, is_en):
        IeCapture.change_zdat_to_txt_for_umac(omm_url, telnet_user_name, telnet_password, signal_trace_path_list, is_en)
    

    @staticmethod
    def change_zdat_to_txt_for_xgw(omm_url, telnet_user_name, telnet_password, signal_trace_path_list, is_en):
        IeCapture.change_zdat_to_txt_for_xgw(omm_url, telnet_user_name, telnet_password, signal_trace_path_list, is_en)

    @staticmethod
    def signal_trace_comparision(signal_trace_path_0,
                                 signal_trace_path_1,
                                 result_path,
                                 tool_path=None):
        logger.info("start signal trace comparision...")
        if not tool_path:
            tool_path = '{0}/../../../tool/signal_compare/InterMsgCmp.exe' \
                .format(os.path.dirname(__file__))
        logger.info('signal trace comparision tool path={0}'.format(tool_path))

        result = SigalTraceComparison(str(signal_trace_path_0),
                                      str(signal_trace_path_1),
                                      str(result_path),
                                      str(tool_path)).compare()
        if result == 0:
            logger.info("result of signal trace comparision is the same")
        elif result < 0:
            logger.warn("result of signal trace comparision is invalid")
        else:
            logger.warn("result of signal trace comparision is different")
        logger.info("end signal trace comparision...")

    @staticmethod
    def change_zdat_to_txt_by_officeline_for_umac(sigtrace_path):
        logger.info('change_zdat_to_txt_by_officeline_for_umac:{0}'.format(sigtrace_path))
        def generate_bat_file(bat_file,sigtrace_path):
            with open(bat_file,'w') as f:
                content = '''@echo off
cd /d "%~dp0"
cd /d "%cd%\"
pvv_st-run.bat "{0}"
                '''.format(sigtrace_path)
                logger.info(content)

                f.write(content)
        def delete_other_files(sigtrace_path):
            file_names=os.listdir(sigtrace_path)
            for file_name in file_names:
                if file_name.lower().endswith('.xls'):
                    os.remove("{0}/{1}".format(sigtrace_path,file_name))

        bat_file = '{0}/../../../traceoffline/generate_st_detail.bat' \
                .format(os.path.dirname(__file__))

        generate_bat_file(bat_file, sigtrace_path)
        os.system(bat_file)
        delete_other_files(sigtrace_path)
    
    @staticmethod    
    def signal_wash(signal_wash_path, sigtrace_path):
        def write_in():
            line = ''.join([' '*4*(level-1),'{0}|--'.format(level),content[i].strip(),'\n'])
            f2.write(line.decode('gbk').encode('utf-8'))
        file_names=os.listdir(sigtrace_path)
        for file_name in file_names:
            if file_name.lower().endswith('.txt'):
                path1 = os.path.join(sigtrace_path,file_name)
                path2 = os.path.join(signal_wash_path,file_name)           
                with open(path1, 'r') as f1:
                    content = f1.readlines()
                    with open(path2, 'a+') as f2:
                        count = 0
                        for i in range(len(content))[4:-1]:
                            if '-------' in content[i+1]:
                                count +=1
                                space_count = {}
                                level = 1
                                line = r'0|--{0} < {1} < {2} :({3})'.format(content[i].split('\t')[2], content[i].split('\t')[4], content[i].split('\t')[3],count)
                                f2.write(line.decode('gbk').encode('utf-8') + '\n')
                                line = r'1|--Detailed: time:{0}, type:{1}'.format(content[i].split('\t')[1], content[i].split('\t')[2])
                                f2.write(line.decode('gbk').encode('utf-8') + '\n')
                                line = r'1|--Detailed: direction:{0}'.format(content[i].split('\t')[3])
                                f2.write(line.decode('gbk').encode('utf-8') + '\n')
                            elif content[i] == '\n' or '----------' in content[i]:
                                f2.write(content[i])        
                            else:                  #剩下消息部分未处理
                            #消息第一行第二行必定为第一层级和第二层级
                                space = [index for index,string in enumerate(content[i]) if not string.isspace()][0] 
                                space_count[i] = space
                                if '-------' in content[i-1]:
                                    write_in()      
                                elif '-------' in content[i-2]:
                                    level+=1
                                    write_in() 
                                else: 
                                    try:    
                                        space_differ = space_count[i]-space_count[i-1]
                                    except: continue
                                    if space_differ == 0 or space_differ == 9 or space_differ == -9:
                                        write_in() 
                                    elif space_differ > 0:
                                        diff = space_differ/4 if space_differ % 4 == 0 else (space_differ-9)/4
                                        level+=diff
                                        write_in()
                                    else:
                                        diff = space_differ/4 if space_differ % 4 == 0 else (space_differ+9)/4
                                        level+=diff
                                        write_in()



                

if __name__ == '__main__':
    # SignalTraceService.change_zdat_to_txt("http://195.137.81.55:2323/combo_mmegngp_sgsn_27/client/#",
    #                                       "admin",
    #                                       "",
    #                                       r"D:\umac_project_version_valid\temp\20160407_161951_combo_mmegngp_sgsn_28\before_upgrade\sigtrace",
    #                                       1)
##    SignalTraceService.signal_trace_comparision(
##        'D:/umac_project_version_valid/temp/20160407_184438_combo_mmegngp_sgsn_28/before_upgrade/sigtrace',
##        'D:/umac_project_version_valid/temp/20160407_184438_combo_mmegngp_sgsn_28/after_upgrade/sigtrace',
##        'D:/umac_project_version_valid/temp/20160407_184438_combo_mmegngp_sgsn_28/before_upgrade/sigtrace',
##        'E:/linxing/ProjectVersionValid_03/tool/signal_compare/InterMsgCmp.exe')
    t1 = time.time()
    print("start change zdat to txt ...")
##        SignalTraceService.change_zdat_to_txt_for_umac(umac_config.omm_url,
##                                              umac_config.telnet_user_name,
##                                              umac_config.telnet_password,
##                                              '{0}[]{1}'.format(umac_config.sigtrace_path_0,
##                                                                umac_config.sigtrace_path_1),
##                                              umac_config.is_en)
    SignalTraceService.change_zdat_to_txt_by_officeline_for_umac(r"E:\umac_project_version_valid\tool\traceoffline\aa")
    time.sleep(5)
    SignalTraceService.change_zdat_to_txt_by_officeline_for_umac(r"E:\umac_project_version_valid\tool\traceoffline\bb")
    print("end change zdat to txt, {0}s".format(time.time() - t1))
