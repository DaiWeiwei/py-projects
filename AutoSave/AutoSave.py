# coding:utf-8

import os
import zipfile
import shutil
import datetime
import glob
import time
import shelve
import json

TODAY = time.strftime('%Y%m%d')
STime = time.time()

conf_path = os.path.join(os.path.dirname(__file__), 'config.json')

with open(conf_path) as f:
    Config = json.load(f)

if os.name == 'nt':
    CurrentOS = 'windows'
    print('CurrentOS:%s' % 'windows')
else:
    CurrentOS = 'linux/unix'
    print('CurrentOS:%s' % 'linux/unix')

Config = Config.get(CurrentOS,None)
LogdataPath = Config.get("LogdataPath",None)
DailyESPath = Config.get("DailyESPath",None)
DBPath = Config.get("DBPath",None)
BackupPath = Config.get("BackupPath",None)
BackupDays = Config.get("BackupDays",None)

def chmod_dir(path):
    if os.path.exists(path):
        os.system("chmod -R 755 %s" % path)
    else:
        os.system("chmod -R 755 %s" % os.path.split(path)[0])

def check_config(*args):
    for arg in args:
        if arg is None:
            raise Exception("Some error was in your config file,please check.")

def get_file_timestamp(file):
    return time.strftime('%Y%m%d', time.localtime(os.stat(file).st_mtime))

def zip_dir(src_dir, dest_dir, filename):
    if not os.path.exists(dest_dir):
        if FirstRun:
            os.makedirs(dest_dir)
        else:
            return
    elif not os.listdir(dest_dir):
        shutil.rmtree(dest_dir)
        return
    else: return
    f = zipfile.ZipFile(os.path.join(dest_dir, filename), 'w', zipfile.ZIP_STORED)
    def trans_files(dir):
        files = glob.glob(os.path.join(dir, '*'))
        for path in files:
            if os.path.isdir(path):
                trans_files(path)
            f.write(path, arcname=path.split(src_dir)[1])
            time.sleep(0.01)
    trans_files(src_dir)
    f.setpassword()
    f.close()
    print('zip dir[%s] and copy to[%s] successfully.' % (src_dir, dest_dir))

def check_first_time():
    global FirstRun
    f = shelve.open(os.path.join(os.path.dirname(__file__), 'isfirst'))
    if not f:
        print('This is first running!')
        FirstRun = True
        f['have_run'] = 'yes'
    else:
        FirstRun = False
    f.close()

def check_date_time(date_time, backup_days, deadline):
    try:
        backup_days = int(backup_days)
    except ValueError:
        # backup all days
        if int(TODAY) - deadline >= int(date_time):
            return True
        return False
    else:
        if int(TODAY) - deadline >= int(date_time) and int(TODAY) - backup_days <= int(date_time):
            return True
        return False

def check_and_zip(root_dir):
    if not os.path.exists(root_dir):
        print('not exist this dir: %s' % root_dir)
        return
    alias_set = os.listdir(root_dir)
    for alias in alias_set:
        wind_machines = os.listdir(os.path.join(root_dir, alias))
        for wind_machine in wind_machines:
            src_dirs = os.listdir(os.path.join(root_dir, alias, wind_machine))
            for src_dir in src_dirs:
                if not os.path.isdir(os.path.join(root_dir, alias, wind_machine, src_dir)):
                    print('this path is not a dir:',os.path.join(root_dir, alias, wind_machine, src_dir))
                    continue
                if check_date_time(src_dir.strip(), BackupDays, 1):
                    zip_dir(os.path.join(root_dir, alias, wind_machine, src_dir),
                            os.path.join(BackupPath,
                                        os.path.split(os.path.split(root_dir)[0])[1],
                                        os.path.split(root_dir)[1],
                                        alias, wind_machine, src_dir),
                            src_dir + '.zip')

def check_and_cut(root_dir):
    if not os.path.exists(root_dir):
        print('not exist this dir: %s' % root_dir)
        return
    all_file = (file for file in os.listdir(root_dir) if file.strip().endswith('.dat'))
    for file in all_file:
        src_path = os.path.join(root_dir, file)
        file_time = get_file_timestamp(src_path)
        if check_date_time(file_time, BackupDays, 3):
            dest_path = os.path.join(BackupPath,
                                     os.path.split(os.path.split(root_dir)[0])[1],
                                     os.path.split(root_dir)[1],
                                     file)
            cut_file(src_path, dest_path)

def cut_file(src_path, dest_path):
    dest_dir = os.path.split(dest_path)[0]
    if not os.path.exists(dest_path):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        os.rename(src_path, dest_path)
        print('cut file[%s] to [%s] successfully.' % (src_path, dest_path))

def compute_elapse_time():
    ETime = time.time()
    elapse_time = ETime - STime
    print('Total elapsed time: %.2fs' % elapse_time)

def main():
    # get_os_info()
    check_config(Config, LogdataPath, DailyESPath, DBPath, BackupPath)
    if not os.path.exists(BackupPath):
        try:
            os.makedirs(BackupPath)
        except:
            chmod_dir(os.path.dirname(BackupPath))
            os.makedirs(BackupPath)
        finally:
            chmod_dir(BackupPath)
    check_first_time()
    check_and_zip(LogdataPath)
    check_and_zip(DailyESPath)
    check_and_cut(DBPath)
    compute_elapse_time()


if __name__ == "__main__":
    main()
    # os.system('pause')
    # print(get_file_timestamp(r'D:\test\1\ss.txt'))
    # zip_dir(r'D:\test\1', r'D:\test\2', '1.zip')


