# -*- coding: utf-8 -*-
import os
import datetime
import subprocess
import json
import requests
from robot.api import logger
from testlib.infrastructure.utility.MyZipFile import create_zip_file
from testlib.infrastructure.utility.FileOperation import FileOperation
from testlib.service.uMacService import uMacService

REST_USER_LOGIN = '/j_spring_security_check'
REST_CMP_FILES = '/comparefiles/process'
REST_CMP_UPLOAD = '/comparefiles/upload'
REST_RULE_UPLOAD = '/comparefiles/ruleupload'
# REST_CMP_UPLOAD_DICT = '/comparefiles/uploaddict'

REST_CMP_DICT = '/comparefiles/customize'
URI_DFS_UPLOAD = '/dfs/upload'
CHROME_EXE = r'"C:\Documents and Settings\Administrator\Local Settings\Application Data\Google\Chrome\Application\chrome.exe"'


# r'"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe"'


class DataAnalysisService(object):
    def __init__(self, home_url='http://10.42.188.28:8080/combo', hdfs_url='hdfs://10.42.188.28:9000', ):
        self.home_url = home_url
        self.hdfs_url = hdfs_url
        self.web_hdfs_url = None
        self.conn = requests.session()
        self.userId = None
        self.connected = False
        self.cmp_rule = None

    #    def loghtml(self, href, text):
    #        logger.debug('*HTML* <a href="%s">%s</a>' % (href, text))

    def combo_close(self):
        self.conn.close()
        self.connected = False

    def abs_url(self, _uri):
        return self.home_url + _uri

    def combo_login(self, username='10129220', password='admin', uri=REST_USER_LOGIN):
        resp = self.conn.post(self.abs_url(uri), data={'j_username': str(username), 'j_password': str(password)})
        if 200 is resp.status_code:
            logger.info('#### :) login success! ####')
            self.connected = True
            self.userId = username
        return self.connected

    # def compare_files_upload_dict(self, contents, uri=REST_CMP_UPLOAD_DICT):
    #     self.conn.post(self.abs_url(uri), json=json.dumps(contents))

    def open_dict_compare(self, uri=REST_CMP_DICT):
        logger.info('###########################################')
        logger.info(u'请使用Chrome浏览器打开如下链接进一步操作: ')
        logger.info('  ' + self.abs_url(uri))
        # webbrowser.open(self.abs_url(uri))
        logger.info('###########################################')
        # subprocess.Popen(self.abs_url(uri), shell=True)

    def zip_file(self, file_path):
        # mod {“base”:"arcname","new":"arcname"}
        # 把基准文件和被比较文件一起压缩传上去
        file_path_split = os.path.split(file_path)
        zip_file = '{0}\\L_{1}_{2}.zip'.format(file_path_split[0],
                                               FileOperation.get_file_name_of_current_time(),
                                               file_path_split[1])
        zip_file = zip_file.replace('\\','/')
        create_zip_file(zip_file, file_path, file_path_split[1])
        return zip_file

    def compare_files_upload(self, base_path=None, new_path=None, uri=REST_CMP_UPLOAD):
        logger.info(u'准备上传')
        if base_path:
            logger.info(u"\t基准文件: " + base_path)
        if new_path:
            logger.info(u"\t待比较文件: " + new_path)
        assert self.connected
        res2 = [None, None]
        if base_path:
            base_zip_file = self.zip_file(base_path, )
            with open(base_zip_file, 'rb') as fb:
                res2[0] = self.conn.post(self.abs_url(uri), files={'cmpbase': fb})
            os.remove(base_zip_file)
        if new_path:
            new_zip_file = self.zip_file(new_path)
            with open(new_zip_file, 'rb') as fn:
                res2[1] = self.conn.post(self.abs_url(uri), files={'cmpnew': fn})
            os.remove(new_zip_file)
        if res2[0] and 200 is not res2[0].status_code:
            logger.info(u'基准文件上传失败!')
        if res2[1] and 200 is not res2[1].status_code:
            logger.info(u'待比较文件上传失败!')
        if not res2[0] and not res2[1]:
            raise AssertionError("上传文件失败!")
        return res2

    def upload_rule_file(self, rule_file=None, uri=REST_RULE_UPLOAD):
        if rule_file:
            logger.info(u"\t规则文件: " + rule_file)
        assert self.connected
        res2 = [None, None]
        if rule_file:
            with open(rule_file, 'rb') as fb:
                res2[0] = self.conn.post(self.abs_url(uri), files={'rule': fb})
        if res2[0] and 200 is not res2[0].status_code:
            logger.info(u'规则文件上传失败!')
        if not res2[0] and not res2[1]:
            raise AssertionError("上传规则文件失败!")
        return res2

    def hdfs_upload_file(self, local_path, remote_path=None):
        logger.info(u'upload_file_hdfs %s to hdfs...' % local_path)
        remote_path = self.hdfs_abs_url(self.userId, os.path.basename(local_path))
        return remote_path

    def compare(self, json_rule=None, uri=REST_CMP_FILES):
        rule = json_rule if json_rule else self.cmp_rule
        assert rule
        res = self.conn.post(self.abs_url(uri), json=json.dumps(rule))
        res_json = json.loads(res.content)
        logger.debug(u'分析报告: ' + res_json['status'])
        return res_json['status']

    def hdfs_abs_url(self, user_id, fname):
        if fname[0] is '/':
            fname = fname[1:]
        return self.hdfs_url + '/user/%s/%s' % (user_id, fname)

    def select_rule(self, id, rule):
        rule_url = None
        # local
        if rule.find(':'):
            logger.info('\tready to upload rule...')
            res = self.upload_rule_file(rule)
            rule_url = ""
        # hdfs
        else:
            rule_url = self.hdfs_abs_url(self.userId, rule)
            logger.debug('\thdfs_abs_url: ' + rule_url)
        # rule_url = self.hdfs_upload_file(rule)
        self.cmp_rule = {"id": id, "rule_url": rule_url, "file_type": "zip"}
        # logger.info(u'比较规则: ' + rule_url)

    def get_report(self, local_path, abs_url):
        res = self.conn.get(abs_url)
        local_fpath = local_path
        if not os.path.isfile(local_fpath):
            local_fpath = os.path.abspath(local_fpath) + datetime.datetime.now().strftime("/report-%Y%m%d-%H%M%S.html")

        with open(local_fpath, 'w') as f:
            f.write(res.content)
        logger.info(u'########################################################################')
        logger.info(u'######## 分析报告已保存至:')
        logger.info(u'######## 本地路径: %s' % local_fpath)
        logger.info(u'########################################################################')
        return local_fpath

    def open_fs_url(self, url):
        subprocess.Popen(' '.join((CHROME_EXE, url)), shell=True)

    def set_web_hdfs_url(self, _url):
        self.web_hdfs_url = _url
        if self.web_hdfs_url[-1] is '/':
            self.web_hdfs_url = self.web_hdfs_url[0:-1]

    def hdfs_list_dir(self, _dir, _operation='LISTSTATUS', username='admin'):
        assert self.web_hdfs_url
        # url = 'http://10.42.188.28:50070/webhdfs/v1/user/10129220/config?op=LISTSTATUS&user.name=admin'
        url = '%s%s?op=%s&user.name=%s' % (self.web_hdfs_url, _dir, _operation, username)
        logger.info('Rest hadoop: ' + url)
        res = requests.get(url)
        return json.loads(res.content)


if __name__ == '__main__':
    rest = DataAnalysisService()
    rest.combo_login()
    rest.compare_files_upload(base_path=r'D:\umac_project_version_valid\temp\v4.10.16.html',
                              new_path=r'D:\umac_project_version_valid\temp\v4.10.18.html')
    rest.select_rule(0, r'D:\umac_project_version_valid\temp\xjr_html_rule.xlsx')
    report_url = rest.compare()
    local_html = rest.get_report(r"D:\umac_project_version_valid\temp", report_url)
    print local_html

    # session_id = rest.conn.cookies.get_dict('10.42.188.28', '/combo').get('JSESSIONID')
    # c = {}
    # with open(r'D:\project\robot\test\1\XGW_COMMON0.txt') as f:
    #     c['base'] = f.read()
    # with open(r'D:\project\robot\test\1\XGW_COMMON1.txt') as f:
    #     c['revised'] = f.read()
    # res = rest.conn.post(rest.abs_url('/comparefiles/uploaddict'), json=json.dumps(c))
    # with open(r'D:\project\robot\test\result.html', 'w') as f:
    #     f.write(res.content)
    # url = rest.home_url + '/comparefiles/customize;JSESSIONID=' + session_id
    # print url
    # subprocess.Popen(ur'"C:\Documents and Settings\Administrator\Local Settings\Application Data\Google\Chrome\Application\chrome.exe" http://10.42.188.28:8080/combo/', shell=True)
    # subprocess.Popen(' '.join((CHROME_EXE, url)), shell=True)
    # rest.combo_close()
    pass
