# coding:utf-8
import re
import os
import shutil

PTN_AP_CFG = re.compile(r'!<APN Configure>(.+?)!</APN Configure>', re.DOTALL)
PTN_AP_ = re.compile(r'\nap\s+|\n\w+-ap\s+', re.DOTALL)

def remove_dir(dir_name,delete_self):
    try:
        shutil.rmtree(dir_name)
    except:
        pass
    if not delete_self:
        os.mkdir(dir_name)

class XgwShowRunning:
    @staticmethod
    def get_show_running(xgw_dut):
        xgw_dut.login()
        xgw_dut.excute_channel_cmd('end', '#', 5)
        xgw_dut.excute_channel_cmd('terminal length 0', '#', 60)
        cmd_result = xgw_dut.excute_channel_cmd('show running-config', '[\w-]+#', 600)
        return cmd_result.return_string

    @staticmethod
    def get_show_running_and_save(xgw_dut,show_running_file):
        show_running_result = XgwShowRunning.get_show_running(xgw_dut)
        with open(show_running_file, 'wb') as f:
            f.write(show_running_result)

##    @staticmethod
##    def pick_apn_configure_from_file(file_path):
##        lines = None
##        with open(file_path, 'r') as f:
##            lines = ''.join(f.readlines())
##
##        dict_configure = {}
##        # global configure
##        XgwShowRunning.analysis_all_global_configure(lines, dict_configure)
##
##        # APN Configure
##                  #'!<APN Configure>.xgw.pgw(.+?)!</APN Configure>'
##        pattern = '<[-\w ]*APN Configure>.xgw.pgw(.+?)!</[-\w ]*APN Configure>'
##        key_name = 'pgwapn'
##        XgwShowRunning.analysis_apn_configure(lines, pattern, key_name, dict_configure)
##        pattern = '<[-\w ]*APN Configure>.xgw.sgw(.+?)!</[-\w ]*APN Configure>'
##        key_name = 'sgwapn'
##        XgwShowRunning.analysis_apn_configure(lines, pattern, key_name, dict_configure)
##        return dict_configure

    @staticmethod
    def classify_config_from_file(file_path):
        lines = None
        with open(file_path, 'r') as f:
            lines = ''.join(f.readlines())

        dict_configure = {}

        #xgw common
        XgwShowRunning.classify_config_of_xgw(lines,dict_configure)
        #xgw pgw
        XgwShowRunning.classify_config_of_pgw(lines,dict_configure)
        #xgw sgw
        XgwShowRunning.classify_config_of_sgw(lines,dict_configure)
        #xgw xdpi
        XgwShowRunning.classify_config_of_xdpi(lines,dict_configure)
        return dict_configure

    @staticmethod
    def pick_and_deal_config(content,pat_str):
        ret = XgwShowRunning.regex_pick(content,pat_str,re.DOTALL)
        return XgwShowRunning.remove_same_and_sepecial(ret)
    @staticmethod
    def classify_config_of_xgw(content,dict_config):
        dict_config['xgw_stu'] = XgwShowRunning.pick_and_deal_config(content,"!<XGW STU Configure>.xgw.stu.(.+?)!</XGW STU Configure>")

    @staticmethod
    def classify_config_of_pgw(content,dict_config):
        ret = XgwShowRunning.regex_pick(content,"!<XGW_PGW>(.+?)!</XGW_PGW>",re.DOTALL)
        content = "\n".join(ret)
        list_pat = [ ['pgw', "!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("XGW PGW Configure")],
                     ['pgw_radius-profile', "!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("Radius Profile Configure")],
                     ['pgw_pcc', "!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("PCC Configure")],
                     ['pgw_pcc_rcp', "!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("Result Code Policy Configure")],
                     ['pgw_cg', "!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("Cg Profile Configure")],
                     ['pgw', "!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("Radius Avp Encode Profile Configure")],
                    #'pgw_apn':"!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("APN Configure"),
                    #'pgw_emrg_apn':"!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("Emergency APN Configure"),
                    #'pgw_rbms_apn':"!<{0}>.xgw.pgw.*?\n(.*?)!</{0}>".format("Rbms APN Configure"),

        ]
        for sub_item in list_pat:
            ret_value = XgwShowRunning.pick_and_deal_config(content,sub_item[1])
            XgwShowRunning._append_to_dict(dict_config,sub_item[0],ret_value)
        #XgwShowRunning.analysis_sub_items_like_apn_configure(content,"^(cg-profile)\s+(\S+)(.+?)\$",'pgw',dict_config)
        #XgwShowRunning.analysis_sub_items_like_apn_configure(content,"^(aaa-profile)\s+(\S+)(.+?)\$",'pgw',dict_config)
        XgwShowRunning.analysis_sub_items_like_apn_configure(content,"^(\w+-ap|ap)\s+(\S+)(.+?)\$",'pgw',dict_config)

    @staticmethod
    def classify_config_of_sgw(content,dict_config):
        ret = XgwShowRunning.regex_pick(content,"!<XGW_SGW>(.+?)!</XGW_SGW>",re.DOTALL)
        content = "\n".join(ret)
        list_pat = [ ['sgw', "!<{0}>.xgw.sgw.*?\n(.*?)!</{0}>".format("XGW SGW Configure")],
                     ['sgw_cg', "!<{0}>.xgw.sgw.*?\n(.*?)!</{0}>".format("Cg Profile Configure")],
                   ]

        for sub_item in list_pat:
            ret_value = XgwShowRunning.pick_and_deal_config(content,sub_item[1])
            XgwShowRunning._append_to_dict(dict_config,sub_item[0],ret_value)

        #XgwShowRunning.analysis_sub_items_like_apn_configure(content,"^(cg-profile)\s+(\S+)(.+?)\$",'sgw',dict_config)
        XgwShowRunning.analysis_sub_items_like_apn_configure(content,"^(\w+-ap|ap)\s+(\S+)(.+?)\$",'sgw',dict_config)

    @staticmethod
    def classify_config_of_xdpi(content,dict_config):
        ret = XgwShowRunning.regex_pick(content,"!<XGW_XDPI>(.+?)!</XGW_XDPI>",re.DOTALL)
        content = "\n".join(ret)
        list_pat = [ ['xdpi', "!<{0}>.xgw.xdpi.*?\n(.*?)!</{0}>".format("XGW XDPI Configure")]
                   ]
        for sub_item in list_pat:
            ret_value = XgwShowRunning.pick_and_deal_config(content,sub_item[1])
            XgwShowRunning._append_to_dict(dict_config,sub_item[0],ret_value)

    #deal for apns,aaa-profile,cg-profile,
    @staticmethod
    def analysis_sub_items_like_apn_configure(content,pattern,key_name,dict_configure):
        segs = XgwShowRunning.regex_pick(content, pattern, re.DOTALL|re.M)
        for seg in segs:
            dict_configure['{0}_{1}#{2}'.format(key_name, seg[0],seg[1])] = XgwShowRunning.remove_same_and_sepecial(seg[2])

    @staticmethod
    def remove_same_and_sepecial(content,sepcial = ['','y','$']):
        #去重
        if type(content) is list:
            content = '\n'.join(content)
        ret = list(set(content.splitlines()))
        if len(sepcial) == 0:
            return
        if type(sepcial) is not list:
            sepcial = [sepcial]
        ret_str = [ x for x in ret if x not in sepcial]
        return '\n'.join(ret_str)

    @staticmethod
    def analysis_show_running_by_apn_and_save(show_running_file,analysis_show_running_file):
        temp_path = os.path.split(analysis_show_running_file)[0]
        temp_analysis_path = temp_path+"/tempdir"
        remove_dir(temp_analysis_path,False)

        dict_apn = XgwShowRunning.classify_config_from_file(show_running_file)
        content = []
        for apn, apn_cfg in dict_apn.items():
            temp = "<{0}>\n{1}\n{2}\n".format(apn, apn_cfg, '*' * 8)
            with open('{0}/{1}.txt'.format(temp_analysis_path,apn),'w') as f:
                f.write(apn_cfg)
            content.append(temp)
        content = ''.join(content)
        #把所有的ap#替换成apn#
        content = re.sub('ap#','apn#',content)
        with open(analysis_show_running_file, 'wb') as f:
            f.write(content)

    @staticmethod
    def pick_apn_configure(content):
        result = {}

        segs = XgwShowRunning.regex_pick(content)
        for seg in segs:
            tt = XgwShowRunning.regex_split(seg)
            aps = tt[1:]
            for ap in aps:
                n = ap.index('\n')
                ap_name = ap[0:n]
                ap_cfg = ap[n + 1:]
                result[ap_name] = ap_cfg
        # MmlLib.save_aps(result)
        return result

    @staticmethod
    def regex_pick(echo, _pattern=PTN_AP_CFG, flags=0):
        segs = []
        _ptn = re.compile(_pattern, flags) if type(_pattern) is str else _pattern
        for ap in _ptn.finditer(echo):
            if len(ap.groups()) == 1:
                segs.append(ap.group(1))
            else:
                segs.append(ap.groups())
        return segs

    @staticmethod
    def regex_split(_str, _pattern=PTN_AP_, flags=0):
        _ptn = re.compile(_pattern, flags) if type(_pattern) is str else _pattern
        return _ptn.split(_str)

    @staticmethod
    def _append_to_dict(dict_config, key_name,key_value):
        if key_name in dict_config:
            dict_config[key_name] = '{0}\n{1}'.format(dict_config[key_name],key_value)
        else:
            dict_config[key_name] = key_value

if __name__ == '__main__':
    from testlib.infrastructure.device.xgw.Xgw import Xgw
    #xgw_dut = Xgw('10.42.188.56')
    show_running_file = r'D:\xgw_project_valid\20160715_105200\before_upgrade\showrunning\show_running.txt'
    out_file =r'D:\xgw_project_valid\20160715_105200\before_upgrade\showrunning\show_running_analysis_result.txt'
    XgwShowRunning.analysis_show_running_by_apn_and_save(show_running_file,out_file)

