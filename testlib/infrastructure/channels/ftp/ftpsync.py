# -*- encoding: utf8 -*-
import os
import sys
import ftplib


class FTPSync(object):
    def __init__(self, host, name, password):
        self.conn = ftplib.FTP(host, name, password)

    def get_dirs_files(self):
        u''' 得到当前目录和文件, 放入dir_res列表 '''
        dir_res = []
        self.conn.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
        return (files, dirs)

    def walk(self, next_dir):
        # print 'Walking to', next_dir
        self.conn.cwd(next_dir)
        # current_local_path = os.getcwd()
        # new_current_local_path = os.path.join(current_local_path,next_dir)
        try:
            os.mkdir(next_dir)
        except OSError:
            pass

        os.chdir(next_dir)
        ftp_curr_dir = self.conn.pwd()
        local_curr_dir = os.getcwd()
        files, dirs = self.get_dirs_files()
        # print "FILES: ", files
        # print "DIRS: ", dirs
        for f in files:
            #print next_dir, ':', f
            outf = open(f, 'wb')
            try:
                self.conn.retrbinary('RETR %s' % f, outf.write)
            finally:
                outf.close()
        for d in dirs:
            os.chdir(local_curr_dir)
            self.conn.cwd(ftp_curr_dir)
            self.walk(d)

    def download(self, local_path, ftp_dirs):
        for dirname in ftp_dirs:
            if not dirname:
                continue
            os.chdir(local_path)
            self.conn.cwd('/')
            self.walk(dirname)

    def upload(self, src_path, dst_dir):
        self.conn.cwd(dst_dir)
        os.chdir(src_path)
        for walker in os.walk(src_path):
            os.chdir(walker[0])
            for filename in walker[2]:
                remote_path = dst_dir + '/' + filename
                fp = open(filename,'rb')
                self.conn.storbinary('STOR '+ remote_path ,fp,1024) #上传文件
                self.conn.set_debuglevel(0)
                fp.close() #关闭文件

    def close(self):
        if self.conn:
            self.conn.close()

def main():
    #local_path = 'd:/111/222/'
    #download_dirs = ['DATA0','vmm']
    local_path = r'D:\111\222\vmm\DATA0'
    f = FTPSync('10.42.188.56', 'zte', 'zte')
    #f.download(local_path, download_dirs)
    f.upload(local_path,'/vmm/test')
    f.close()

if __name__ == '__main__':
    main()
