# coding:utf-8
import struct
import re


class XgwSoftPara:
    @staticmethod
    def get_and_save_soft_para_to_file(xgw_dut, soft_para_file):
        soft_para = XgwSoftPara._get_soft_para(xgw_dut)
        XgwSoftPara._save_soft_para_to_file(soft_para, soft_para_file)

    @staticmethod
    def _get_soft_para(xgw_dut):
        xgw_dut.login()
        XgwSoftPara._go_to_super_model(xgw_dut)
        xgw_soft_para = XgwSoftPara._get_type_soft_para(xgw_dut, ['end', 'con t', 'xgw'])
        sgw_soft_para = XgwSoftPara._get_type_soft_para(xgw_dut, ['end', 'con t', 'xgw', 'sgw'])
        pgw_soft_para = XgwSoftPara._get_type_soft_para(xgw_dut, ['end', 'con t', 'xgw', 'pgw'])
        xdpi_soft_para = XgwSoftPara._get_type_soft_para(xgw_dut, ['end', 'con t', 'xgw', 'xdpi'])

        return {'xgw': xgw_soft_para,
                'sgw': sgw_soft_para,
                'pgw': pgw_soft_para,
                'xdpi': xdpi_soft_para
                }

    @staticmethod
    def _save_soft_para_to_file(soft_para, soft_para_file):
        with open(soft_para_file, 'w') as f:
            f.write('#softpara index currentid default\n')
            for _type, _soft_para_value in soft_para.items():
                f.write('<{0}>\n'.format(_type))
                for line in _soft_para_value:
                    f.write('softpara {0} {1} {2}\n'.format(line[0], line[1],line[2]))
                f.write('*' * 8+'\n')

    @staticmethod
    def _get_type_soft_para(xgw_dut, pre_cmd_list):
        assert (len(pre_cmd_list) > 0)
        for cmd in pre_cmd_list:
            xgw_dut.excute_channel_cmd(cmd, '#', 2)
        result = xgw_dut.excute_channel_cmd('list-softpara', '#', 300)
        if not result:
            return []
        return re.findall("^(\d+)\s+(\d+)\s+(\d+)", result.return_string, re.M)

    @staticmethod
    def _go_to_super_model(xgw_dut):
        cmd_list = ['olleh', 'super-en 16', XgwSoftPara._get_ctrl_c()]
        for cmd in cmd_list:
            xgw_dut.excute_channel_cmd(cmd, '#', 2)

    @staticmethod
    def _get_ctrl_c():
        ctrlc_bytes = struct.pack('B', 3)
        ctrlc_bytes += struct.pack('B', 0)
        return ctrlc_bytes


if __name__ == '__main__':
    from testlib.infrastructure.device.xgw.Xgw import Xgw

    xgw_dut = Xgw('10.42.188.56')
    XgwSoftPara.get_and_save_soft_para_to_file(xgw_dut, "c:/soft_para.txt")
