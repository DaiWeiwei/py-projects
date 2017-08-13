# coding:utf-8

import os
from lxml import etree as ET
# try:
#     import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET
from testlib.infrastructure.netmanagementxml.NetManagementCommand import NetManagementCommand
from testlib.infrastructure.netmanagementxml.CommandParam import CommandParam


class NetManagementXml(object):
    def __init__(self, command_names, mml_dir, is_cn):
        self._command_names = command_names
        self._mml_dir = mml_dir
        self._is_cn = is_cn
        self._net_management_commands = {}
        self._needed_cmd_info_files = []
        self._dict_cmd_info_files_to_commands = {}
        self._cmd_info_files_has_enum = []
        # self._analysis_xml_files()

    # 返回命令的行头
    def get_command_label_values(self, command):
        pass

    def _load_command_label_values(self):
        for cmd_info_files in self._needed_cmd_info_files:
            cmd_info_i18n_file = cmd_info_files.replace('-cmdinfo.xml', '-cmdinfo-i18n.xml')
            self._load_command_label_values_from_cmd_info_i18n(cmd_info_i18n_file)

    def _load_command_label_values_from_cmd_info_i18n(self, cmd_info_i18n_file):
        pass

    def _get_cmd_info_files_of_needed_commands(self):
        dict_commands_to_cmd_info_file = self._match_command_names_from_all_cmd_info_files(self._mml_dir)
        for command_name in self._command_names:
            net_management_command = NetManagementCommand(command_name, dict_commands_to_cmd_info_file[command_name])

    def _analysis_xml_files(self):
        self._load_needed_command_info_from_all_cmd_info_files(self._mml_dir)

    @staticmethod
    def _get_all_cmd_info_files(mml_dir):
        cmd_info_files = []
        for parent_path, dirs, fs in os.walk(mml_dir):
            for f in fs:
                if not f.lower().endswith('-mml-cmdinfo.xml'):
                    continue
                cmd_info_files.append(os.path.join(parent_path, f))
        return cmd_info_files

    def _is_needed_command(self, command_name):
        return command_name in self._command_names

    def _load_needed_command_info_from_file(self, cmd_info_file):
        try:
            tree = ET.parse(cmd_info_file)
            root = tree.getroot()
            command_names = []
            has_enum_out_param = False
            for command_tag in root.findall('command'):
                name = command_tag.find('name').text
                if not self._is_needed_command(name):
                    continue
                net_management_command = NetManagementCommand(name, cmd_info_file)
                params_tag = command_tag.find('outparams').findall('param')
                for param in params_tag:
                    command_param = CommandParam()
                    command_param.parse(param)
                    if command_param.is_enum():
                        has_enum_out_param = True
                    net_management_command.out_params.append(command_param)
                command_names.append(name)
                self._net_management_commands[name] = net_management_command
            self._dict_cmd_info_files_to_commands[cmd_info_file] = command_names
            if has_enum_out_param:
                self._cmd_info_files_has_enum.append(cmd_info_file)
        except Exception, e:
            print "Error:cannot parse file:", cmd_info_file

    def _load_all_needed_command_info(self):
        cmd_info_files = self._get_all_cmd_info_files(self._mml_dir)
        for cmd_info_file in cmd_info_files:
            if self._load_needed_command_info_from_file(cmd_info_file):
                self._needed_cmd_info_files.append(cmd_info_file)

    def _load_all_needed_command_info_i18n(self):
        for cmd_info_file in self._needed_cmd_info_files:
            cmd_info_i18n_file = cmd_info_file.replace('-cmdinfo.xml', '-cmdinfo-i18n.xml')
            self._load_needed_command_info_from_cmd_info_file(cmd_info_i18n_file)

    def _load_needed_command_info_i18n_from_file(self, file_name):
        command_names = self._dict_cmd_info_files_to_commands.get(file_name, [])
        if not command_names:
            return
        for command_name in command_names:
            ne_management_command = self._net_management_commands[command_name]
            for param in ne_management_command.out_params:
                if self._is_cn:
                    pass
                else:
                    pass



def get_net_management_commands():
    with open('c:/commands.txt', 'r') as f:
        return f.readlines()
    return []


umac_commands = get_net_management_commands()
nm = NetManagementXml(umac_commands, r'F:\umac_mml\mml', False)
nm._load_all_needed_command_info()

# import time
#
# t1 = time.time()
# dict_commands_to_file = get_command_names_from_all_cmdinfo_files(r'F:\umac_mml\mml')
# umac_commands = get_net_management_commands()
#
# for command in umac_commands:
#     if not command in dict_commands_to_file:
#         print 'cannot find command [{0}] from xml files'.format(command)
#         continue
#
# print time.time() - t1
# print r
