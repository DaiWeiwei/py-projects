# coding=utf-8
from testlib.infrastructure.utility.ByteArrayStringOperaion import ByteArrayStringOperaion


class ParamUtility(object):
    NO_EXIST = ""
    DEFAULT = "Default_value"

    @staticmethod
    def build_params(value_names, values):
        info = {}
        for value_name, value in zip(value_names, values):
            if ParamUtility.is_not_operate(value):
                continue
            elif ParamUtility.is_no_exist(value):
                info[value_name] = None
            else:
                info[value_name] = value
        return info

    @staticmethod
    def build_param_with_len(value_name, value_len_name, value):
        if ParamUtility.is_not_operate(value):
            return {}
        info = {}
        if ParamUtility.is_no_exist(value):
            info[value_name] = None
        else:
            info[value_len_name], info[value_name] = ParamUtility._even_imputation(value)
        return info

    # TODO 删除带flag相关接口
    @staticmethod
    def build_params_with_flag(value_flag_names, value_names, values):
        info = {}
        for value_flag_name, value_name, value in zip(value_flag_names, value_names, values):
            if ParamUtility.is_not_operate(value):
                continue
            if ParamUtility.is_no_exist(value):
                info[value_flag_name] = 0
            else:
                info[value_flag_name] = 1
                info[value_name] = value
        return info

    @staticmethod
    def build_params_with_flag_and_len(value_flag_names, value_names, value_len_names, values):
        info = {}
        for value_flag_name, value_name, value_len_name, value \
                in zip(value_flag_names, value_names, value_len_names, values):
            sub_info = ParamUtility.build_param_with_flag_and_len(value_flag_name, value_name,
                                                                  value_len_name, value)
            info.update(sub_info)
        return info

    @staticmethod
    def build_param_with_flag_and_len(value_flag_name, value_name, value_len_name, value):
        if ParamUtility.is_not_operate(value):
            return {}
        info = {}
        if ParamUtility.is_no_exist(value):
            info[value_flag_name] = 0
        else:
            info[value_flag_name] = 1
            info[value_len_name], info[value_name] = ParamUtility._even_imputation(value)
        return info

    @staticmethod
    def is_no_exist(param):
        return param == ParamUtility.NO_EXIST

    @staticmethod
    def is_not_operate(param):
        return param is None or param == {} or param == []

    @staticmethod
    def is_default(param):
        return param == ParamUtility.DEFAULT

    @staticmethod
    def is_ip_format(param):
        return ParamUtility.is_ipv4_format(param) or ParamUtility.is_ipv6_format(param)

    @staticmethod
    def is_ipv4_format(param):
        # todo 后续改为正则严格判断是否为ip格式
        return param.find('.') != -1

    @staticmethod
    def is_ipv6_format(param):
        return param.find(':') != -1

    @staticmethod
    def to_int(param):
        if isinstance(param, basestring) and param.isdigit():
            return int(param)
        return param

    @staticmethod
    def to_list(param):
        if isinstance(param, basestring):
            return eval(param)
        raise Exception("input param[{0}] is not list format string.".format(param))

    @staticmethod
    def all_param_is_no_exist(*params):
        for param in params:
            if param != ParamUtility.NO_EXIST:
                return False
        return True

    @staticmethod
    def _even_imputation(value):
        if not isinstance(value, basestring):
            return 0, ""

        length = len(value)
        if ParamUtility._is_even(length):
            return length / 2, value

        value += '0'
        return (length + 1) / 2, value

    @staticmethod
    def to_byte_array_string(in_str):
        if in_str is None:
            return None
        return ByteArrayStringOperaion.convert_string_to_byte_array_string(in_str)


    @staticmethod
    def _is_even(digit):
        return not (digit % 2)

    @staticmethod
    def _build_para_list(value):
        if not value or ParamUtility.is_no_exist(value):
            return value
        value = [item.strip() for item in value.strip('[').strip(']').split(',')]
        return [{'Class': ParamUtility.to_byte_array_string(item)} for item in value]

    @staticmethod
    def hex_format(dec_number):
        if dec_number is None:
            return None

        hex_number = '0x' + ''.join(list('0' * (16 - len(list(hex(int(dec_number)))[2:])))
                                    + list(hex(int(dec_number)))[2:])
        return hex_number

    @staticmethod
    def _construct_para_list(para_list):
        para_list_v = ''
        for para in para_list:
            if para is None:
                continue
            para_hex = (lambda x: ''.join(list('0' * (16 - len(list(hex(int(x)))[2:])))
                                        + list(hex(int(x)))[2:]))(para)
            para_list_v += para_hex
        return para_list_v

    @staticmethod
    def change_to_hex_str(int_str, with_0x=False, max_len=-1, padding_0_from_left=True):
        if int_str is None:
            return None
        hex_str = hex(int(int_str))
        if not with_0x:
            hex_str = hex_str[2:]
        return ByteArrayStringOperaion.fill_zero(hex_str, max_len, padding_0_from_left)

