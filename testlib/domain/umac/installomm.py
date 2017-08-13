#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      10022510
#
# Created:     07-11-2016
# Copyright:   (c) 10022510 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# _*_ coding: utf-8 _*_
import sys
import os
import time
from utils.ssh2lib import ssh2
from utils.file_operating import File_Opereating
PATHABS_NOW = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(os.path.abspath(PATHABS_NOW))
from utils.mylogger import mylogger

class installomm(object):

    def __init__(self,omm_verinfo):
        self.logger = mylogger.getlogger("Install OMM")
        self.omm_verinfo = omm_verinfo
        self.local_oldver_path=os.path.join(PATHABS_NOW.replace('process\..',''),"version\\oldversion\\")
        self.local_newver_path=os.path.join(PATHABS_NOW.replace('process\..',''),"version\\newversion\\")
        self.remote_ver_path='/home/autorelease/ommversion'
        self.remote_sh_path='/home/autorelease/ommsh'
        self.remote_data_path='/home/autorelease/ommversion/data'
        self.install_sh=os.path.join(PATHABS_NOW.replace('process\..',''),"version\\install_new_omm.sh")
        self.xml=os.path.join(PATHABS_NOW.replace('process\..',''),"version\\macro-infos.xml")


    def excute(self):
        install_result='OK'
        lic_oldfile, omm_oldfile, agent_oldfile=self.check_local_file(self.local_oldver_path,self.omm_verinfo['Old_version_no'].lower())
        lic_newfile, omm_newfile, agent_oldfile=self.check_local_file(self.local_newver_path,self.omm_verinfo['New_version_no'].lower())
        if len(lic_oldfile)==0 or len(omm_oldfile)==0 or len(lic_newfile)==0 or len(omm_newfile)==0:
            install_result='NOK'
            return install_result

        #安装老版本


        if self.omm_verinfo ['Old_install']=='y' :

            self.logger.info( "Connect old OMM server %s for install!"%self.omm_verinfo['Old_host'])
            self.logger.info( "Install old omm server")
            self.ssh=ssh2(self.omm_verinfo['Old_host'],22,'root',self.omm_verinfo['Old_rootpass'])
            self.check_remote_file()
            self.logger.info( "Upload OMM version to server%s"%omm_oldfile)
            self.upload_file_to_omm(omm_oldfile,self.remote_ver_path+'/'+omm_oldfile.split('\\')[-1])
            self.logger.info( "Upload OMM version to server successfully")
            self.logger.info("Upload agent version to server%s"%agent_oldfile)
            self.upload_file_to_omm(agent_oldfile,self.remote_ver_path+'/'+agent_oldfile.split('\\')[-1])
            self.logger.info( "Upload agent version to server successfully")
  ##          self.start_installagent() #启动安装代理
  ##          return
            # self.install_ommversion(self.omm_verinfo['old_neid'],self.omm_verinfo['Omm_oldnetype'])

            #加载license
            old_remote_lice='/home/ngomm/'+self.omm_verinfo['Omm_oldnetype']+'/server/conf/license/'+lic_oldfile.split('\\')[-1]
            self.upload_file_to_omm(lic_oldfile,old_remote_lice)
             #加载重启网管
            try:
                self.stop_omm()
            except Exception,e:
                self.logger.info(e)
                self.ssh=ssh2(self.omm_verinfo['Old_host'],22,'root',self.omm_verinfo['Old_rootpass'])
                self.stop_omm()
            try:
                self.start_omm()
            except Exception,e:
                self.logger.info(e)
                self.ssh=ssh2(self.omm_verinfo['Old_host'],22,'root',self.omm_verinfo['Old_rootpass'])
                self.start_omm()
           #关闭链接
            self.install_over()

        
        return install_result



    def check_local_file(self,path,omm_version):
        lic_count=0
        omm_count=0
        agent_count=0
        lic_file=''
        omm_file=''
        agent_file=''
        for filename in os.listdir(path):
            omm_filename=filename.lower()
            if omm_filename.endswith('.lic'):
                lic_count+=1
                lic_file=os.path.join(path,filename)

            elif omm_filename.endswith('.tar.gz'):
                if omm_filename.find(omm_version)!=-1:
                    omm_count+=1
                    omm_file=os.path.join(path,filename)
                elif omm_filename.find('installagent')!=-1:
                    agent_count+=1
                    agent_file=os.path.join(path,filename)

            elif omm_filename == 'data':
                self.upload_data_file(path+'\\DATA')

        if not lic_count or not omm_count or not agent_count:
            self.logger.info( "License file or omm version file or agent file is not correct!")
      
        return lic_file, omm_file, agent_file

    def start_omm(self):
        cmd_result,cmd_err=self.ssh.ssh_exec_cmd("ps -ef | grep HA")
        if cmd_result.find('NewStartHA'):
            stdin,stdout,stderr=self.ssh.ssh_cmd_sh("nshares -start ngomm_app")
            while not stdout.channel.exit_status_ready():
                self.logger.info("Please wait for minutes...,now is starting HA!")
                time.sleep(50)
            self.logger.info("Starting HA is over!")
        else:
            cmd_result,cmd_err=self.ssh.ssh_exec_cmd("find /nec_script -name 'omm_start.sh' -print")
            if len(cmd_result)==0:
               cmd_result,cmd_err=self.ssh.ssh_exec_cmd("find /ommscripts -name 'omm_start.sh' -print")
            self.logger.info(len(cmd_result))
            if len(cmd_result)==0:
                stdin,stdout,stderr=self.ssh.ssh_cmd_sh("/home/ngomm/run.sh")
                while not stdout.channel.exit_status_ready():
                    self.logger.info("Please wait for minutes...,now is restarting OMM!")
                    time.sleep(50)
                self.logger.info("Starting OMM is over！")
            else :
                stdin,stdout,stderr=self.ssh.ssh_cmd_sh("clprsc -s omm_exec")
                while not stdout.channel.exit_status_ready():
                    self.logger.info("Please wait for minutes...,now is starting omm_exec of cluster OMM!")
                    time.sleep(10)
                stdin,stdout,stderr=self.ssh.ssh_cmd_sh("clprsc -s swd_mon_exec")
                while not stdout.channel.exit_status_ready():
                    self.logger.info("Please wait for minutes...,now is starting swd_mon_exec of cluster OMM!")
                    time.sleep(10)
                self.logger.info("Starting cluster OMM is over！")
            time.sleep(60)


    def check_remote_file(self):
        #先清空目录，再创建目录

        self.ssh.ssh_exec_cmd('rm -rf /home/autorelease')
        self.logger.info( "Create directory for install")
        self.ssh.mkdir('/home/autorelease')
        self.logger.info( "Create directory of autorelease ok")
        self.ssh.mkdir('/home/autorelease/ommversion')
        self.logger.info( "Create directory of ommversion ok")
        self.ssh.mkdir('/home/autorelease/ommsh')
        self.logger.info( "Create directory of ommsh ok")
        self.ssh.mkdir('/home/autorelease/ommversion/data')
        self.logger.info( "Create directory of restored datas ok")
        self.ssh.upload_file_to_remote(self.install_sh,self.remote_sh_path+'/install_new_omm.sh')
        self.ssh.upload_file_to_remote(self.xml,self.remote_ver_path+'/macro-infos.xml')
        self.ssh.ssh_exec_cmd('chmod -R 777 /home/autorelease')
        self.logger.info( "Directory fot installation is created successfully!")


    def upload_data_file(self,data_dir):
        self.logger.info("Start uploading restored data files")
        # s = ssh2(self.omm_verinfo['Old_host'],22,'root',self.omm_verinfo['Old_rootpass'])
        for file in os.listdir(data_dir):
            try:
                self.upload_file_to_omm(os.path.join(data_dir,file),os.path.join(self.remote_data_path,file))
            except Exception,e:
                self.ssh=ssh2(self.omm_verinfo['Old_host'],22,'root',self.omm_verinfo['Old_rootpass'])
                self.upload_file_to_omm(os.path.join(data_dir,file),os.path.join(self.remote_data_path,file))
                
        # s.close()

        self.logger.info("Upload restored data files successfully")



    def upload_file_to_omm(self,local_file,remote_file):
        self.logger.info( "Upload file,local_file is %s"%local_file)
        self.logger.info( "Upload file,remote_file is %s"%remote_file)
        self.ssh.upload_file_to_remote(local_file,remote_file)


    def install_ommversion(self,neid,netype):
        ommtype=netype
        if netype.find('combo_mmegngp_sgsn')!=-1:  #combo
            netype='0x7FFFFFFF00002000'
        if netype.find('gngp_sgsn')!=-1 and netype.find('mmegngp_sgsn')==-1:
            netype='0x7FFFFFFF00000001'
        if netype.find('mme')!=-1 and netype.find('mmegngp_sgsn')==-1:
            netype='0x7FFFFFFF00000100'

        servid=100000+ int(neid)
        servid=str(servid)
        stdin,stdout,stderr=self.ssh.ssh_cmd_sh("/home/autorelease/ommsh/install_new_omm.sh "+ommtype+' '+neid+' '+servid+' '+netype)
        self.logger.info("Install omm :"+"/home/autorelease/ommsh/install_new_omm.sh "+ommtype+' '+neid+' '+servid+' '+netype)

        while not stdout.channel.exit_status_ready():
            self.logger.info('Please wait for minutes...,now is install neid %s' %neid)
            time.sleep(60)
        self.logger.info("end install new OMM %s" %neid)
        self.logger.info("Del version file after installation!")
        try:
            self.ssh.ssh_exec_cmd('rm -rf /home/autorelease/ommversion/*')
        except Exception,e:
            self.logger.info(e)
            self.ssh=ssh2(self.omm_verinfo['Old_host'],22,'root',self.omm_verinfo['Old_rootpass'])
            self.ssh.ssh_exec_cmd('rm -rf /home/autorelease/ommversion/*')


    def install_over(self):

        self.ssh.close()
        self.logger.info("Close sftp connection")

    def stop_omm(self):
        cmd_result,cmd_err=self.ssh.ssh_exec_cmd("ps -ef | grep HA")
        if cmd_result.find('NewStartHA'):
            stdin,stdout,stderr=self.ssh.ssh_cmd_sh("nshares -stop ngomm_app")
            while not stdout.channel.exit_status_ready():
                self.logger.info("Please wait for minutes...,now is stopping HA!")
                time.sleep(50)
            self.logger.info("Stopping HA is over!")
        else:
            cmd_result,cmd_err=self.ssh.ssh_exec_cmd("find /nec_script -name 'omm_start.sh' -print")
            if len(cmd_result)==0:
               cmd_result,cmd_err=self.ssh.ssh_exec_cmd("find /ommscripts -name 'omm_start.sh' -print")

            self.logger.info(len(cmd_result))
            if len(cmd_result)==0:
                stdin,stdout,stderr=self.ssh.ssh_cmd_sh("/home/ngomm/killall.sh")
                while not stdout.channel.exit_status_ready():
                    self.logger.info("Please wait for minutes...,now is stopping OMM!")
                    time.sleep(50)
                self.logger.info("Stopping OMM is over!")

            else :
                stdin,stdout,stderr=self.ssh.ssh_cmd_sh("clprsc -t swd_mon_exec")  #停止监控资源组
                while not stdout.channel.exit_status_ready():
                    self.logger.info("Please wait for minutes...,now is stopping swd_mon_exec of cluster OMM!")
                    time.sleep(10)
                stdin,stdout,stderr=self.ssh.ssh_cmd_sh("clprsc -t omm_exec")  #停止网管资源组
                while not stdout.channel.exit_status_ready():
                    self.logger.info("Please wait for minutes...,now is stopping omm_exec of cluster OMM!")
                    time.sleep(10)
                self.logger.info("Stopping  cluster OMM is over!")
            time.sleep(60)

    def start_installagent(self):
        stdin,stdout,stderr=self.ssh.ssh_cmd_sh("cd /home/installagent/run.sh")
        while not stdout.channel.exit_status_ready():
              self.logger.info("Please wait for minutes...,now is starting installagent!")
              time.sleep(3)
        self.logger.info("Starting installagent is over!")



if __name__ == "__main__":
    myomm=installomm()

    print 'www'


