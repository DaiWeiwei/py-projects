# coding=utf-8
import cPickle
from testlib.infrastructure.phonebook.phonebookoperate import PhoneBookOperate
from testlib.infrastructure.utility.DictUtility import DictUtility
from testlib.infrastructure.serviceconfig.serviceconfigoperate import ServiceConfigOperate
import re
from robot.api import logger
from testlib.infrastructure.utility.ParamUtility import ParamUtility

SERIAL_NUMBER_ALL = -1
MSG_ALL = "all_msg"


class CommDataArea(object):
    """
    request_field, expect_field理解示例
    {
        'CrSessRes': {
            -1: {"tIndicationFlags", {"blCRSI": 1, "blP": 1}},   # -1:表示对所有CrSessRes有效
            1：{"tCause": {"enCause": 16},                       #  1:表示对后面第一条CrSessRes有效,一次有效
                "enPeerQos": 1},
            3: {"enPeerQos": 0}
        },
        'ModBearRes': {
            1：{"tCause": {"enCause": 18}}
        },
        'all_msg': {                        # all_msg:表示可以对所有消息
            -1: {"tCause": {"enCause": 18}}
        }
    }
    """

    def __init__(self, name=''):
        self._name = name
        self._short_name = self._name.replace('User.user', '.u').replace('session', 's').replace('bear', 'b')
        self._init_fields = {}  # 初始化数据和自动保存数据
        self._set_fields = {}  # 用户关键字设置的数据
        self._expect_fields = {}  # 用户关键字设置的期望
        self._successful_expect_fields = {}  # 默认设置的期望（成功消息才检查的期望值，如果失败响应则不检查）
        self._condition_fields = {}

    def init_field(self, key, value, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        self._set_x_field(self._init_fields, msg_type, key, value, serial_number)

    def set_field(self, key, value, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        result,new_value = self._set_x_field(self._set_fields, msg_type, key, value, serial_number)
        if not result:
            return
        print_key = key if msg_type is None or msg_type == MSG_ALL else msg_type+'.'+key
        logger.info('{0:13} {1:8} {2:40}\t{3}'.format(self._short_name, 'Set:', print_key+':', new_value))

    def clear_all(self):
        self._expect_fields.clear()
        self._set_fields.clear()
        self._successful_expect_fields.clear()
        self._condition_fields.clear()

    @staticmethod
    def merge_fields(fields, new_fields):
        if fields is None and new_fields is None:
            return None
        result_fields = {}
        if fields is not None:
            result_fields = DictUtility.deep_copy_dict(fields)
        DictUtility.update_dict(result_fields, new_fields)
        return result_fields

    def _update_x_field(self, x_fields, key, value, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        fields = self._get_x_fields(x_fields, msg_type, serial_number)
        field = fields.get(key) if fields else None
        if type(field) is not dict or type(value) is not dict:
            self._set_x_field(x_fields, msg_type, key, value, serial_number)
            return
        DictUtility.update_dict(field, value)

    def update_init_field(self, key, value, msg_type=MSG_ALL):
        self._update_x_field(self._init_fields, key, value, msg_type, SERIAL_NUMBER_ALL)

    def update_field(self, key, value, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        self._update_x_field(self._set_fields, key, value, msg_type, serial_number)

    def clear_field(self, key, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        set_fields = self._get_set_fields(msg_type, serial_number)
        if set_fields and key in set_fields:
            set_fields.pop(key)

    def get_field(self, key, default=None, msg_type=MSG_ALL, serial_number=None):
        comm_fields = self._get_merged_fields(self._init_fields, msg_type)
        set_fields = self._get_merged_fields(self._set_fields, msg_type)
        fields = self.merge_fields(comm_fields, set_fields)
        field = DictUtility.get_field(fields, key)
        return field if field is not None else default

    @staticmethod
    def update_field_serial_number(fields):
        for (i, field) in fields.items():
            if i == SERIAL_NUMBER_ALL:  # 表示对所有该消息有效，不删除
                continue
            del fields[i]
            fields[i - 1] = field

    def _set_x_field_ex(self, x_fields, msg_type, key, value, serial_number=1):
        fields = x_fields.get(msg_type)
        if fields is None:
            x_fields[msg_type] = {}
        field = x_fields[msg_type].get(serial_number)
        if field is None:
            x_fields[msg_type][serial_number] = {}
        if '.' in key:
            DictUtility.update_dict(x_fields[msg_type][serial_number],
                                    DictUtility.gen_dict_from_key_value_str(key, value))
            return
        x_fields[msg_type][serial_number][key] = value

    def _trans_value(self, value):
        if ParamUtility.is_not_operate(value):
            return False, None
        if ParamUtility.is_no_exist(value):
            return True, None
        return True, self._handle_special_char(value)

    def _set_x_field(self, x_fields, msg_type, key, value, serial_number=1):
        result, value = self._trans_value(value)
        if not result:
            return False,value
        if msg_type is None:
            msg_type = MSG_ALL
        serial_number = SERIAL_NUMBER_ALL if serial_number is None else int(serial_number)
        if isinstance(msg_type, list):
            for msg_type_item in msg_type:
                self._set_x_field_ex(x_fields, msg_type_item, key, value, serial_number)
        else:
            self._set_x_field_ex(x_fields, msg_type, key, value, serial_number)
        return True, value

    @staticmethod
    def _get_x_fields(fields, msg_type, serial_number=SERIAL_NUMBER_ALL):
        if msg_type is None:
            msg_type = MSG_ALL
        serial_number = int(serial_number) if serial_number else SERIAL_NUMBER_ALL
        fields = fields.get(msg_type)
        return fields.get(serial_number) if fields else None

    def _get_x_field(self, x_fields, key, default=None, msg_type=None, serial_number=SERIAL_NUMBER_ALL):
        fields = self._get_x_fields(x_fields, msg_type, serial_number)
        return fields.get(key, default) if fields else default

    def _get_set_fields(self, msg_type, serial_number=SERIAL_NUMBER_ALL):
        return self._get_x_fields(self._set_fields, msg_type, serial_number)

    def get_init_field(self, key, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        return self._get_x_field(self._init_fields, key, None, msg_type, serial_number)

    def get_set_field(self, key, default=None, msg_type=MSG_ALL, serial_number=SERIAL_NUMBER_ALL):
        return self._get_x_field(self._set_fields, key, default, msg_type, serial_number)

    def _get_merged_fields_ex(self, x_fields, msg_type, delete_fields=False):
        fields = x_fields.get(msg_type)
        if not fields:
            return {}
        repeatedly_field = fields.get(SERIAL_NUMBER_ALL, {})
        one_off_field = fields.get(1, {})
        if delete_fields:
            if one_off_field:
                del fields[1]
            CommDataArea.update_field_serial_number(fields)
        return self.merge_fields(repeatedly_field, one_off_field)

    def _get_merged_fields(self, x_fields, msg_type, delete_fields=False):
        comm_fields = self._get_merged_fields_ex(x_fields, MSG_ALL, delete_fields)
        msg_fields = {}
        if msg_type != MSG_ALL:
            msg_fields = self._get_merged_fields_ex(x_fields, msg_type, delete_fields)
        return self.merge_fields(comm_fields, msg_fields)

    def set_condition_field(self, msg_type, key, value, serial_number=1):
        self._set_x_field(self._condition_fields, msg_type, key, value, serial_number)

    def get_condition_fields(self, msg_type):
        return self._get_merged_fields(self._condition_fields, msg_type, delete_fields=True)

    def set_expect_field(self, msg_type, key, value, serial_number=1):
        if msg_type is None:
            raise Exception("set expect: msg_type parameter must be set.")
        result, new_value = self._set_x_field(self._expect_fields, msg_type, key, value, serial_number)
        if type(msg_type) is not list:  # list情况是默认设置，不是用户设置，不必log
            logger.info('{0:13} {1:8} {2:40}\t{3}'.format(
                self._short_name, 'Expect:', str(msg_type)+'.'+key+':', new_value))

    def get_expect_fields(self, msg_type):
        return self._get_merged_fields(self._expect_fields, msg_type, delete_fields=True)

    def set_successful_expect_field(self, msg_type, key, value, serial_number=SERIAL_NUMBER_ALL):
        self._set_x_field(self._successful_expect_fields, msg_type, key, value, serial_number)

    def get_successful_expect_fields(self, msg_type):
        return self._get_merged_fields(self._successful_expect_fields, msg_type, delete_fields=True)

    def get_expect_field(self, msg_type, key, default=None, serial_number=1):
        return self._get_x_field(self._expect_fields, key, default, msg_type, serial_number)

    def query_expect_field(self, msg_type, serial_number=None):
        fields = self._expect_fields.get(msg_type)
        if not fields:
            return None
        if serial_number is None:
            return fields
        else:
            return fields.get(serial_number)

    def fill_msg_by_module(self, parameters, msg_type, msg_module, deal_disposable_field=False):
        if self._init_fields:
            logger.debug("{0:22} {1:20} {2}".format(self._short_name, "init_fields", self._init_fields))
        if self._set_fields:
            logger.debug("{0:22} {1:20} {2}".format(self._short_name, "set_fields", self._set_fields))
        if msg_module is None:
            return
        init_fields = self._get_merged_fields(self._init_fields, msg_type)
        self._fill_msg_parameters_by_module_ex(parameters, init_fields, msg_module, deal_disposable_field, False)
        set_parameters = {}
        set_fields = self._get_merged_fields(self._set_fields, msg_type, delete_fields=True)
        self._fill_msg_parameters_by_module_ex(set_parameters, set_fields, msg_module, deal_disposable_field, True)
        DictUtility.update_dict(parameters, set_parameters)

    def _fill_msg_parameters_by_module_ex(self, parameters, fields, msg_module,
                                          deal_disposable_field=False, delete_disposable_field=False):
        if deal_disposable_field:
            self._fill_msg_parameters_by_module(parameters, fields, msg_module.get("normal"))
            self._fill_msg_parameters_by_module(parameters, fields, msg_module.get("disposable"),
                                                delete_disposable_field)
        else:
            self._fill_msg_parameters_by_module(parameters, fields, msg_module)

    def _fill_msg_parameters_by_module(self, parameters, fields, msg_module, delete_disposable_field=False):
        if msg_module is None or fields is None:
            return
        for (name_in_msg, name_in_domain) in msg_module.items():
            if type(name_in_domain) is dict:
                if not parameters.get(name_in_msg):
                    parameters[name_in_msg] = {}
                self._fill_msg_parameters_by_module(parameters[name_in_msg], fields, name_in_domain,
                                                    delete_disposable_field)
                continue
            if name_in_domain in fields:
                parameters[name_in_msg] = fields.get(name_in_domain)
                if delete_disposable_field:
                    self.clear_field(name_in_domain)

    def fill_condition(self, condition, msg_module, need_delete=False):
        if msg_module is None:
            return
        for (name_in_msg, name_in_domain) in msg_module.items():
            if type(name_in_domain) is dict:
                if not condition.get(name_in_msg):
                    condition[name_in_msg] = {}
                self.fill_condition(condition[name_in_msg], name_in_domain, need_delete)
                continue
            value = self.get_field(name_in_domain)
            if value is not None:
                condition[name_in_msg] = value
                if need_delete:
                    self.clear_field(name_in_domain)

    def init_by_module(self, init_module):
        init_module1 = cPickle.loads(cPickle.dumps(init_module, -1))
        for scope, fields in init_module1.items():
            if scope == 'global':
                for name, value in fields.items():
                    self.init_field(name, value)
            else:
                for name, value in fields.items():
                    self.init_field(name, value, scope)

    def check_no_expect_left(self):
        for (msg_name, msg_expect) in self._expect_fields.items():
            for (serial_number, expect) in msg_expect.items():
                if serial_number != SERIAL_NUMBER_ALL:
                    logger.warn("{0:13} {1:8} {2:20} expect({3})".format(
                        self._short_name, 'have expect not check:', msg_name+'['+str(serial_number)+']', expect))
                    logger.warn("{0:13} {1:8} ".format(
                        self._short_name, 'have expect not check, please check test case script.'))

    def check_expect_ex(self, msg, msg_parameters=None, expect_parameters=None):
        if not expect_parameters:
            return
        try:
            logger.info("{0:13} {1:8} {2:20} expect({3})".format(self._short_name, 'Check:', msg.type, expect_parameters))
            return msg.check_expect_parameters(expect_parameters, msg_parameters)
        except Exception, e:
            raise Exception("{0:12} check expect fail, ".format(self._short_name) + e.message)

    def check_expect(self, msg, msg_parameters=None):
        if self._expect_fields:
            logger.debug("{0:22} {1:20} {2}".format(self._short_name, "expect_fields", self._expect_fields))
        self.check_expect_ex(msg, msg_parameters, self.get_expect_fields(msg.type))

    def check_successful_expect(self, msg, msg_parameters=None):
        if self._successful_expect_fields:
            logger.debug("{0:22} {1:20} {2}".format(self._short_name, "succ_expect_fields",
                                                    self._successful_expect_fields))
        self.check_expect_ex(msg, msg_parameters, self.get_successful_expect_fields(msg.type))

    def save_field_from_msg(self, msg, module={}, parameters=None):
        if parameters is None:
            parameters = msg.parameters
        if msg.is_response():
            if msg.is_fail():
                return
        self.check_successful_expect(msg, parameters)
        if module is None:
            return
        self.save_field_by_module(parameters, module.get("required"), True)
        self.save_field_by_module(parameters, module.get("optional"), False)

    def save_field_by_module(self, parameters, field_module, is_required):
        if field_module is None:
            return
        for (name_in_msg, name_in_domain) in field_module.items():
            if type(name_in_domain) is dict:
                self.save_field_by_module(parameters.get(name_in_msg), name_in_domain, is_required)
                continue
            if name_in_msg is None:
                self.save_field(name_in_domain, parameters, is_required)
            else:
                if parameters is not None:
                    self.save_field(name_in_domain, parameters.get(name_in_msg), is_required)

    def save_field(self, key, value, is_required=True):
        if value is None:
            if is_required:
                raise Exception("receive message: required parameter[{0}] is not found.".format(key))
            return
        if key is None:
            return
        self.init_field(key, value)

    def save_optional_field(self, key, value):
        self.save_field(key, value, False)

    def _sub_special_refer(self, value, begin_char, end_char, func):
        result = re.findall(begin_char + r'([\w|\.|\-|\[|\]]+)' + end_char, value)
        if result:
            for x in result:
                book_value = str(func(x))
                x = self._sub_pattern_special_char(x)
                sub_value = re.sub(begin_char + x + end_char, book_value, value)
                value = sub_value
            return sub_value
        return value

    def _sub_single_percent(self, value):
        return self._sub_special_refer(value, '%', '$', PhoneBookOperate().get_attr)

    def _sub_double_percent(self, value):
        return self._sub_special_refer(value, '%', '%', PhoneBookOperate().get_attr)

    def _sub_single_amp(self, value):
        return self._sub_special_refer(value, '&', '$', self.get_field)

    def _sub_double_amp(self, value):
        return self._sub_special_refer(value, '&', '&', self.get_field)

    def _sub_single_pound(self, value):
        return self._sub_special_refer(value, '#', '$', ServiceConfigOperate().get_attr)

    def _sub_double_pound(self, value):
        return self._sub_special_refer(value, '#', '#', ServiceConfigOperate().get_attr)

    def _sub_pattern_special_char(self, value):
        return value.replace('[', '\[').replace(']', '\]').replace('.', '\.').replace('-', '\-')

    def _handle_special_char(self, value):
        if isinstance(value, basestring) and ("%" in value or "&" in value or "#" in value):
            value = self._sub_single_percent(value)
            value = self._sub_double_percent(value)
            value = self._sub_single_amp(value)
            value = self._sub_single_pound(value)
            value = self._sub_double_pound(value)
        return value
