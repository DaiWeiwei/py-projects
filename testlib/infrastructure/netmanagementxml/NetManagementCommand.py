from testlib.infrastructure.netmanagementxml.CommandParam import CommandParam
class NetManagementCommand(object):
    def __init__(self, command_name, cmd_info_file):
        self.en_label_values = []
        self.cn_label_values = []
        self.cmdinfo_file = cmd_info_file
        self.command_name = command_name
        self.out_params = []
