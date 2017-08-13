# -*- coding: utf-8 -*-
import paramiko
import threading
import time
import os
import re
from robot.api import logger
from testlib.infrastructure.utility.FileOperation import FileOperation

class UmacOmm(object):
    def __init__(self, omm_ip, username, password):
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(omm_ip, 22, username, password, timeout=5)

        t = paramiko.Transport((omm_ip, 22))
        t.connect(username=username, password=password)
        self._sftp = paramiko.SFTPClient.from_transport(t)

        self._local_omm_agent_file = ''
        self._local_omm_version_file = ''

    def close(self):
        try:
            if self._ssh:
                self._ssh.close()
            if self._sftp:
                self._sftp.close()
        except:
            pass


    def _get_local_agent_version_file(self,local_path):
        agent_version_files = self._get_local_files(local_path,".tar.gz","installagent.")
        if not agent_version_files:
            raise Exception("cannot find agent version in {0},please check it!".format(local_path))
        return agent_version_files[0]

    def _get_local_omm_version_file(self,local_path):
        local_files = self._get_local_files(local_path,".tar.gz","ZXUN_uMAC")
        if not local_files:
            raise Exception("cannot find omm version in {0},please check it!".format(local_path))
        return local_files[0]

    def _get_local_agent_version_no(self):
        m = re.search('installagent(.+)tar.gz',self._local_omm_agent_file,re.I)
        return m.group(1).strip('.')

    def _get_omm_agent_version_no(self):
        logger.debug('run shell:cat /home/installagent/agent/conf/comcfg.ini')
        stdin, stdout, stderr = self._ssh.exec_command('cat /home/installagent/agent/conf/comcfg.ini')
        return_string = ''.join(stdout.readlines())
        #logger.debug('result:{0}'.format(return_string))
        m = re.search('Version=(.+)',return_string)
        if not m:
           raise Exception("cannot find omm agent version, please check it")
        return m.group(1).strip(' \r\n')

#xjr添加，获取服务器上的网管显示版本号
    def _get_omm_version_no(self,command):

        omm_version=''
        logger.info(command)
        stdin, stdout, stderr = self._ssh.exec_command(command)
        return_string = ''.join(stdout.readlines())
        #logger.debug('result:{0}'.format(return_string))
##        logger.info(return_string)
        len_return=len(return_string.strip())
        if len_return>0:
            vershow_pos=return_string.strip().split("verShow=")[1]
##            logger.info(str(vershow_pos))
##            logger.info(str(len_return))

            omm_version=vershow_pos.split('"')[1]

            logger.info(omm_version)

        return omm_version



#xjr添加0530，删除当前网元
    def _delete_cur_omm(self,neid):
        template = '#!/bin/bash\ncd /home/installagent/agent\n./qsetup -d -n'+neid+'\n'
##        logger.info(template)
        file_name = '{0}/{1}'.format(os.getcwd(), 'del_omm_netype.sh')
        with open(file_name, 'wb') as f:
            f.write(template)
        self.upload_file_to_remote_dir(file_name, '/')
        sh_file = '/del_omm_netype.sh'
        self._sftp.chmod(sh_file, 0777)
        stdin, stdout, stderr = self._ssh.exec_command(sh_file)
        while not stdout.channel.exit_status_ready():
            logger.info('del omm version, please wait for minutes...')
            time.sleep(60)
        logger.info('end del omm version')

#xjr添加0531，新装网元
    def _install_new_omm(self,omm_version_path,neid,netype):
        if netype=='Combo MME/GnGp SGSN':
            netype='0x7FFFFFFF00002000'
        if netype=='GnGp SGSN':
            netype='0x7FFFFFFF00000001'
        if netype=='MME':
            netype='0x7FFFFFFF00000100'
##        ./qsetup -i$OMMVERSIONPATH -q -n252 -v100355 -t0x7FFFFFFF00002000 -fComm2011
        servid=100000+ int(neid)
        servid=str(servid)
##        logger.info(servid)

        template = '#!/bin/bash\nOMMVERSIONPATH=`ls {0}/ZXUN_uMAC*.tar.gz`\ncd /home/installagent/agent\necho "install new omm"\n./qsetup -i$OMMVERSIONPATH -q -n{1} -v{2} -t{3} -fComm2011\necho "end setup"'.format(
            omm_version_path, neid,servid,netype)
##        logger.info(template)
        file_name = '{0}/{1}'.format(os.getcwd(), 'install_new_omm.sh')
        with open(file_name, 'wb') as f:
            f.write(template)
        self.upload_file_to_remote_dir(file_name, '/')
        sh_file = '/install_new_omm.sh'
        self._sftp.chmod(sh_file, 0777)
        stdin, stdout, stderr = self._ssh.exec_command(sh_file)
        while not stdout.channel.exit_status_ready():
            logger.info('install new OMM, please wait for minutes...')
            time.sleep(60)
        logger.info('end install new OMM')




    @staticmethod
    def _format_agent_version_no(agent_version):
        re_agent = re.search('(\d+).(\d+).(\d+).P(\d+).B(\d+)(.*)',agent_version,re.I)
        agent_temp = '{:0>2}.{:0>2}.{:0>2}.{:0>2}.{:0>2}'.format(re_agent.group(1),
                                                                  re_agent.group(2),
                                                                  re_agent.group(3),
                                                                  re_agent.group(4),
                                                                  re_agent.group(5))
        agent_temp += re_agent.group(6)
        return agent_temp
    @staticmethod
    def _compare_agent_version_no(local_agent_version,omm_agent_version):
        local_agent_format = UmacOmm._format_agent_version_no(local_agent_version)
        omm_agent_format  = UmacOmm._format_agent_version_no(omm_agent_version)
        logger.debug("local agent:{0};omm agent:{1}".format(local_agent_format,omm_agent_format))
        return local_agent_format > omm_agent_format

    def _check_omm_upload(self):
        local_agent_version_no = self._get_local_agent_version_no()
        omm_agent_version_no = self._get_omm_agent_version_no()
        return self._compare_agent_version_no(local_agent_version_no,omm_agent_version_no)

    def _get_local_omm_agent_and_version(self,local_path):
        self._local_omm_agent_file = self._get_local_agent_version_file(local_path)
        self._local_omm_version_file = self._get_local_omm_version_file(local_path)
        print 'agent:',self._local_omm_agent_file
        print 'omm:',self._local_omm_version_file
    def _backup_omm_agent(self):
        logger.info('start backup omm agent')
        cmd = 'mv /home/installagent /home/installagent_{0}'.format(FileOperation.get_file_name_of_current_time())
        stdin, stdout, stderr = self._ssh.exec_command(cmd)
        logger.info('end backup omm agent')

    def upgrade_omm_agent_and_version(self, office_id, local_path):
        logger.info('start upgrade omm agent and version...')

        self._get_local_omm_agent_and_version(local_path)
        remote_path = '/home/version/omm'
        self.delete_dir(remote_path)
        remote_path = '/home/version'
        self.create_remote_dir(remote_path)
        remote_path = '/home/version/omm'
        self.create_remote_dir(remote_path)
        #if local agent verision > omm agent version,upload local omm agent and upgrade
        upgrade_omm_agent_flag = False
        if(self._check_omm_upload()):
            #backup agent first
            logger.info('start upload omm agent')
            self.upload_file_to_remote_dir("{0}\\{1}".format(local_path,self._local_omm_agent_file),remote_path)
            logger.info('end upload omm agent')
            upgrade_omm_agent_flag = True
        logger.info('start upload omm version')
        self.upload_file_to_remote_dir("{0}\\{1}".format(local_path,self._local_omm_version_file),remote_path)
        logger.info('end upload omm version')
        if upgrade_omm_agent_flag:
            self._backup_omm_agent()
            self.upgrade_omm_agent()
            time.sleep(10)
        self.upgrade_omm_version(office_id,remote_path)

    def upgrade_omm_agent(self):
        logger.info('start upgrade omm agent')
        file_name = self._save_upgrade_agent_file()
        self.upload_file_to_remote_dir(file_name, '/')

        sh_file = '/upgrade_omm_agent.sh'
        self._sftp.chmod(sh_file, 0777)
        stdin, stdout, stderr = self._ssh.exec_command(sh_file)
        while not stdout.channel.exit_status_ready():
              time.sleep(5)
        logger.info('end upgrade omm agent')

    def upgrade_omm_version(self, office_id, omm_version_path):
        logger.info('start upgrade omm version')
        file_name = self._save_upgrade_omm_file(office_id, omm_version_path)
        self.upload_file_to_remote_dir(file_name, '/')

        sh_file = '/upgrade_omm_version.sh'
        self._sftp.chmod(sh_file, 0777)
    
        stdin, stdout, stderr = self._ssh.exec_command(sh_file)
        while not stdout.channel.exit_status_ready():
            logger.info('upgrading omm version, please wait for minutes...')
            time.sleep(60)
        logger.info('end upgrade omm version')

    def install_omm(self,umac_config):
        umac_config.src_omm_version_no
        umac_config.src_omm_path
        umac_config.restored_data
        remote_omm_path = '/home/version'
        remote_sh_path = '/home/version/sh'
        remote_data_path = 'home/version/data'

        

    def delete_dir(self, dirname, delete_self=False):
        try:
##            logger.info(dirname)
            if not dirname:
##                logger.info("wwww")
                return
            self._sftp.chmod(dirname, 0777)
            cmd = "rm -rf " + dirname
##            logger.info("tttt")

            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            while not stdout.channel.exit_status_ready():
                time.sleep(5)
            if not delete_self:
                self._sftp.mkdir(dirname, 0777)
##                logger.info("yyyy")

        except:
##            logger.info("rrrr")
            pass

    def create_remote_dir(self, dirname):
        try:
##            logger.info(dirname+'wwwwwww')
            self._sftp.mkdir(dirname, 0777)

        except:
            pass

    def upload_file_to_remote_dir(self, filename, dst_path):
        if dst_path == '/':
            dst_file_name = '/{0}'.format(os.path.split(filename)[1])
        else:
            dst_file_name = '{0}/{1}'.format(dst_path, os.path.split(filename)[1])

        self.upload_file_by_sftp(filename, dst_file_name)

    def upload_file_by_sftp(self, src_file, dst_file):
        logger.info(" upload file {0} to {1}".format(src_file, dst_file))
        self._sftp.put(src_file, dst_file)

    def upload_dir_files_to_remote_dir(self, local_dir, remote_dir, file_suffix = ""):
        local_files = self._get_local_files(local_dir, file_suffix)
        if not local_files:
            return 0
        t = time.time()
        logger.info("start upload files to remote...")
        logger.info("upload from {0}".format(local_dir))
        logger.info("upload to {0}".format(remote_dir))
        for filename in local_files:
            local_file = os.path.join(local_dir, filename).replace("\\", "/")
            remote_file = os.path.join(remote_dir, filename).replace("\\", "/")
            self.upload_file_by_sftp(local_file, remote_file)
        logger.info("end upload files to remote, {0}ms".format(time.time() - t))
        return len(local_files)
    
    def upload_service_version_files(self, src_path, dst_path):
        self.create_remote_dir(dst_path)
        local_version_files = self._get_local_service_version_files(src_path, 'SBCW_')
        if not local_version_files:
            raise Exception("no local service version files in {0}".format(src_path))
        for filename in local_version_files:
            local_file = os.path.join(src_path, filename).replace("\\", "/")
            remote_file = os.path.join(dst_path, filename).replace("\\", "/")
            self.upload_file_by_sftp(local_file, remote_file)

    # 下载基础函数
    def download_file_by_sftp(self, localpath, remotepath):
        self._sftp.get(remotepath, localpath)
    
# 删除所有文件
    def delete_dir_files(self, remotepath):
        if not os.path.exists(remotepath):
            return

        files=self._sftp.listdir(remotepath)
        if (len(files)>0):
          for fn in files:
            #删除该目录下所有文件
             remotefile=os.path.join(remotepath,fn).replace('\\','/')

             cmd='rm -rf '+remotefile
             self._ssh.exec_command(cmd)


    @staticmethod
    #return simple file names
    def _get_local_files(local_path,file_suffix='',file_prefix = ''):
        os.chdir(os.path.split(local_path)[0])
        parent = os.path.split(local_path)[1]
        local_files = []
        for walker in os.walk(parent):
            for filename in walker[2]:
                if file_suffix and not filename.lower().endswith(file_suffix):
                    continue
                if file_prefix and not filename.startswith(file_prefix):
                    continue
                local_files.append(filename)
        return local_files
    @staticmethod
    #return simple file names
    def _get_local_files_exclude_prefix(local_path,file_suffix='',exclude_file_prefix = ''):
        os.chdir(os.path.split(local_path)[0])
        parent = os.path.split(local_path)[1]
        local_files = []
        for walker in os.walk(parent):
            for filename in walker[2]:
                if file_suffix and not filename.lower().endswith(file_suffix):
                    continue
                if exclude_file_prefix and filename.startswith(exclude_file_prefix):
                    continue
                local_files.append(filename)
        return local_files

#xjr添加20160614，获取服务器上的网管内部版本号和日期
    def get_omm_interversion(self,command):

        stdin, stdout, stderr = self._ssh.exec_command(command)
        return_string = ''.join(stdout.readlines())

        m = re.findall('(\d\.\d+.\d+)',return_string)

        if len(m)>0 :
           omm_version= int(m[0].replace('.',''))
##        logger.info(m[0])
        cmd_date= 'date +%Y%m%d '
        stdin, stdout, stderr = self._ssh.exec_command(cmd_date)
        return_string =  ''.join(stdout.readlines())
        curr_date=int(return_string.strip()[6:8])
        para_label=int(omm_version/curr_date)
        return str(para_label)
