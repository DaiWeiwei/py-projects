# coding=utf-8
import re
from robot.api import logger


class DictUtility(object):

    @staticmethod
    def is_sub_dict(parent_dict, sub_parameters, raise_exception=False):
        try:
            return DictUtility._is_sub_dict(parent_dict, sub_parameters, log_compare_result=raise_exception)
        except Exception, e:
            if raise_exception:
                raise Exception("{0}".format(e))
            else:
                logger.debug(e)
                return False

    @staticmethod
    def _is_sub_dict(parent_dict, sub_parameters, log_compare_result=False):
        if sub_parameters is None:
            return True
        for (k, v) in sub_parameters.items():
            parent_parameter = DictUtility.get_field(parent_dict, k)
            if v is None:
                if parent_parameter is not None:
                    raise Exception("{0}: expect({1}), actual({2}).".format(k, v, parent_parameter))
                else:
                    continue
            if parent_parameter is None:
                raise Exception("{0}: not found.".format(k))
            if DictUtility.is_expression(v):
                if not DictUtility.expression_matching(parent_parameter, v):
                    raise Exception("{0}: expect({1}), actual({2}).".format(k, v, parent_parameter))
            elif isinstance(v, dict):
                try:
                    DictUtility._is_sub_dict(parent_parameter, v)
                except Exception, e:
                    raise Exception("{0}.{1}".format(k, e))
            elif isinstance(v, list) and isinstance(parent_parameter, list):
                for expect_x in v:
                    for msg_x in parent_parameter:
                        if DictUtility.is_sub_dict(msg_x, expect_x):
                            break
                    else:
                        raise Exception("{0}: expect({1}), actual({2}).".format(k, v, parent_parameter))
            else:
                if not DictUtility.is_equal(parent_parameter, v):
                    raise Exception("{0}: expect({1}), actual({2}).".format(k, v, parent_parameter))
            # if log_compare_result:
            #     logger.info("{0:8} {1:20} key({2}) | expect({3}) | actual({4}).".format('Result:','success',k, v, parent_parameter))
        return True

    @staticmethod
    def is_expression(expect_value):
        return isinstance(expect_value, basestring) and str.startswith(str(expect_value).strip(), "exp(")

    @staticmethod
    def expression_matching(value, expect_value):
        # todo 后续表达式比较支持放到该函数实现  表达式格式： exp(表达式)
        return DictUtility.is_equal(value, expect_value)

    @staticmethod
    def is_equal(value, expect_value):
        if isinstance(expect_value, list):
            return value in expect_value
        if isinstance(value, int) and not isinstance(expect_value, int) and\
                not expect_value.startswith(("!=", ">", "<", "[")):
            expect_value = int(expect_value)

        if not isinstance(expect_value, basestring) or not \
                expect_value.startswith(("!=", ">", "<", "[")):
            return value == expect_value
        # 属性值比较支持表达式处理
        if not isinstance(value, (basestring, int)):
            return False
        if isinstance(value, int) or value.isdigit():  # 123 或者 “123”
            try:
                return eval(str(value) + expect_value)
            except:
                return value == expect_value
        else:  # “abc”
            if expect_value.startswith("!="):
                return value != expect_value[2:]
            elif expect_value.startswith(">"):
                return value > expect_value[1:]
            elif expect_value.startswith("<"):
                return value < expect_value[1:]
            elif expect_value.startswith("["):
                return value in eval(expect_value)
            else:
                return value == expect_value

    @staticmethod
    def update_dict(old_dict, new_dict):
        """ 两个嵌套字典的 更新合并 new_dict合并到old_dict中 """
        # if new_dict is None:
        #     return
        if type(old_dict) is not dict or type(new_dict) is not dict:
            raise Exception("update_dict: param is not dict, old_dict is [{0}], new_dict is [{1}]".format(old_dict, new_dict))
        for k, v in new_dict.items():
            old_item = old_dict.get(k)
            if old_item and type(old_item) is dict and type(v) is dict:
                DictUtility.update_dict(old_item, v)
            else:
                old_dict[k] = v

    @staticmethod
    def deep_copy_dict(_dict):
        """ 字典的深拷贝，遍历拷贝，避免引用拷贝导致的数据修改 """
        result_dict = {}
        if _dict is None:
            return None
        for k, v in _dict.items():
            if type(v) is dict:
                v = DictUtility.deep_copy_dict(v)
            result_dict[k] = v
        return result_dict

    @staticmethod
    def get_field(data, key):
        if not isinstance(data, dict):
            return None
        if '.' in key:
            keys = key.split('.')
            if '[' in keys[0] and ']' in keys[0]:
                k = re.search(r'(.*?)(\[.*\])', keys[0]).group(1)
                i = re.search(r'(.*?)(\[.*\])', keys[0]).group(2)
                v = None
                exec_str = 'v=data.get("%s")%s' % (k, i)
                exec(exec_str)
            else:
                v = data.get(keys[0])
            return DictUtility.get_field(v, '.'.join(keys[1:]))
        elif '[' in key and ']' in key:
            k = re.search(r'(.*?)(\[.*\])', key).group(1)
            i = re.search(r'(.*?)(\[.*\])', key).group(2)
            v = None
            exec_str = 'v=data.get("%s")%s' % (k, i)
            exec(exec_str)
            return v
        else:
            return data.get(key)

    @staticmethod
    def get_field_byDict(data, dictfield):
        if not isinstance(data, dict) or not isinstance(dictfield, dict):
            return None
        
    @staticmethod
    def transfer_to_list(data_dict):
        DictUtility.transfer_to_list_recursion(data_dict)

    @staticmethod
    def transfer_to_list_recursion(data_dict, last_dict=None, last_k=None):
        if isinstance(data_dict, dict):
            count = 0
            for k, v in data_dict.items():
                if '[' in k:
                    index = re.search(r'\[(\d+)\]', k).group(1)
                    value_list = []
                    value_list.append(v)
                    if count == 0:
                        last_dict[last_k] = value_list
                    else:
                        last_dict[last_k].append(v)
                    del data_dict['[' + index + ']']
                    count += 1
                DictUtility.transfer_to_list_recursion(v, data_dict, k)

    @staticmethod
    def remove_none_values_in_dict(dict_data):
        dict_result = {}
        for (key, value) in dict_data.items():
            if value is not None:
                dict_result.update({key: value})
        return dict_result

    @staticmethod
    def gen_dict_from_key_value_str(key, value):
        ks = ['"%s"' % x for x in key.split('.')]
        ks.append('value')
        ks.reverse()
        dict_str = reduce(lambda x, y: '{%s: %s}' % (y, x), tuple(ks))
        return eval(dict_str)