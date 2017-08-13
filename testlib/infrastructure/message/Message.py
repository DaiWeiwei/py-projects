# coding=utf-8
from contextlib import contextmanager
import json
import re
import time
from testlib.infrastructure.message.MessageModule import IS_RESPONSE, SUCCESS_CODE, PARAMETER_STRUCT_NAME
from testlib.infrastructure.utility.DictUtility import DictUtility
from testlib.infrastructure.utility.Exception import (MessageParamNotFoundException, MessageCheckException)


class Message(object):
    _LINK_IN_MESSAGE = 'link'
    _TYPE_IN_MESSAGE = 'type'
    _PROTOCOL_IN_MESSAGE = 'protocol'
    _MESSAGE_TYPE_IN_MESSAGE = 'message'
    _PARAMETERS_IN_MESSAGE = 'parameters'
    _MESSAGE_LIST_IN_MESSAGE = 'message'
    _BEAR_IN_MESSAGE = 'bear'

    def __init__(self, operate_type="send message", link=None, protocol=None, message_type=None, message_name=None,
                 parameters=None, module={}, bear={}):
        self._timestamp = time.clock()
        self._operate_type = operate_type
        self._link = link
        self._protocol = protocol
        self._type = message_type
        self._module = module
        self._parameters_struct_name = message_name if message_name else module.get("struct_alias")
        self._parameters = parameters
        self._path_stack = []
        if parameters is None:
            self._parameters = {}
        self._bear = bear

    @property
    def type(self):
        return self._type

    @property
    def operate_type(self):
        return self._operate_type

    @property
    def module(self):
        return self._module

    def set_module(self, msg_module):
        self._module = msg_module

    @property
    def parameters(self):
        return self._parameters

    @property
    def link(self):
        return self._link

    @property
    def bear(self):
        return self._bear

    @bear.setter
    def bear(self, value):
        self._bear = value

    def __str__(self):
        return json.dumps(self.encode(), indent=True)

    def set_parameter(self, key, value):
        if value is not None:
            self._parameters[key] = value

    def is_response(self):
        return self._module.get(IS_RESPONSE)

    def is_fail(self):
        success_code = self.module.get(SUCCESS_CODE)
        if success_code is not None and not DictUtility.is_sub_dict(self._parameters, success_code):
            return True
        return False

    def encode_message_body(self):
        if re.search(r'.*?\'\[\d+\]\':', str(self._parameters)):
            DictUtility.transfer_to_list(self._parameters)
        message_body = {
            Message._PROTOCOL_IN_MESSAGE: self._protocol,
            Message._MESSAGE_TYPE_IN_MESSAGE: self._type,
            Message._PARAMETERS_IN_MESSAGE: {self._parameters_struct_name: self._parameters}
        }
        return message_body

    @staticmethod
    def encode_multiple_msg(msgs):
        msg_bodys = []
        for msg in msgs:
            msg_bodys.append(msg.encode_message_body())
        multiple_msg = {
            Message._TYPE_IN_MESSAGE: msgs[0].operate_type,
            Message._LINK_IN_MESSAGE: msgs[0].link,
            Message._BEAR_IN_MESSAGE: msgs[0].bear,
            Message._MESSAGE_LIST_IN_MESSAGE: msg_bodys
        }
        return multiple_msg

    def encode(self):
        msg_body = self.encode_message_body()
        msg = {
            Message._TYPE_IN_MESSAGE: self._operate_type,
            Message._LINK_IN_MESSAGE: self._link,
            Message._BEAR_IN_MESSAGE: self._bear,
            Message._MESSAGE_LIST_IN_MESSAGE: [msg_body]
        }
        return msg

    def check_expect_parameters(self, expect_parameters, msg_parameters=None):
        if not expect_parameters:
            return True
        parameter_struct_name = self.module.get(PARAMETER_STRUCT_NAME)
        if parameter_struct_name:
            expect_parameters = {parameter_struct_name: expect_parameters}
        if msg_parameters is None:
            msg_parameters = self.parameters

        if re.search(r'.*?\'\[\d+\]\':', str(expect_parameters)): # TODO: 删除
            DictUtility.transfer_to_list(expect_parameters)
        return DictUtility.is_sub_dict(msg_parameters, expect_parameters, raise_exception=True)

    @staticmethod
    def decode_parameters_from_message_layer(msg_layer):
        return Message.get_first_value_of_dict(msg_layer.get(Message._PARAMETERS_IN_MESSAGE))

    @staticmethod
    def get_first_value_of_dict(dict_value):
        if not dict_value:
            return None
        return dict_value[dict_value.keys()[0]]

    @staticmethod
    def decode(msg):
        link = msg.get(Message._LINK_IN_MESSAGE)
        _type = msg.get(Message._TYPE_IN_MESSAGE)
        msg_list_in_message = msg.get(Message._MESSAGE_LIST_IN_MESSAGE)

        if not msg_list_in_message:
            return []
        msg_decode = []
        for msg_layer in msg_list_in_message:
            protocol = msg_layer.get(Message._PROTOCOL_IN_MESSAGE)
            message_type = msg_layer.get(Message._MESSAGE_TYPE_IN_MESSAGE)
            parameters = Message.decode_parameters_from_message_layer(msg_layer)
            msg_decode.append(Message(operate_type=_type,
                                      link=link,
                                      protocol=protocol,
                                      message_type=message_type,
                                      message_name="",
                                      parameters=parameters))
        return msg_decode

    def __setitem__(self, key, value):
        self.set_param(key, value)

    def __getitem__(self, key):
        return self.get_param(key, True)

    def _get_param_path(self, items, create=True):
        '''
        根据key查找对应的参数字典存放的位置
        '''
        if len(self._path_stack) > 0:
            current_path = self._path_stack[-1]
        else:
            current_path = self._parameters

        for item in items:
            pos = item.find('[')
            if pos == -1:
                if item not in current_path:
                    if create:
                        current_path[item] = {}
                    else:
                        return None
                current_path = current_path[item]
                if not isinstance(current_path, dict):
                    return None
            else:
                try:
                    index = int(item[pos + 1:-1])
                except ValueError:
                    index = len(current_path)
                item = item[:pos]
                if item not in current_path:
                    if create:
                        current_path[item] = []
                    else:
                        return None
                current_path = current_path[item]
                if index >= len(current_path):
                    if create:
                        current_path.insert(index, {})
                    else:
                        return None
                current_path = current_path[index]
                if not isinstance(current_path, dict):
                    return None

        return current_path

    def set_param(self, path, value):
        if value is None:
            return
        items = path.split('.')
        path = self._get_param_path(items[:-1], True)
        if path is None:
            raise MessageParamNotFoundException(self, path)
        path[items[-1]] = value

    def get_param(self, path, check=False):
        items = path.split('.')
        path_found = self._get_param_path(items[:-1], False)
        if path_found is not None and items[-1] in path_found:
            return path_found[items[-1]]
        elif check:
            raise MessageParamNotFoundException(self, path)
        return None

    @contextmanager
    def open_param_path(self, path, create=True):
        items = path.split('.')
        path_found = self._get_param_path(items, create)
        if path_found is None:
            raise MessageParamNotFoundException(self, path)

        self._path_stack.append(path_found)
        try:
            yield
        finally:
            self._path_stack.pop()

    @staticmethod
    def check(actual, expect, path):
        if actual != expect:
            raise MessageCheckException(actual, expect, path)
