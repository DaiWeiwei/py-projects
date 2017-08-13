# coding=utf-8
import os
from testlib.infrastructure.resource.resource.adapter import yaml
from testlib.infrastructure.utility.Singleton import Singleton

ALIAS = "alias"

RECEIVE_CONDITION = "receive_condition"
COMMON_RECEIVE_CONDITION = "common_receive_condition"
IS_RESPONSE = "is_response"
SUCCESS_CODE = "success_code"

FIX = "fix"
SESSION = "session"
BEAR = "bear"
USER = "user"

DEAL_CREATE = "CREATE"
DEAL_REMOVE = "REMOVE"
DEAL_MODIFY = "MODIFY"

ID_CODE = "id_code"

PARAMETER_STRUCT_NAME = "parameter_struct_name"


@Singleton
class MessageModule(object):

    def __init__(self):
        self._modules = {}

    @property
    def modules(self):
        return self._modules

    def get(self, ne_type):
        msg_modules = self._modules.get(ne_type)
        if msg_modules is None:
            f = open(os.path.dirname(__file__) +
                     '/modulefile/'+ne_type.title()+'.yml')
            msg_modules = yaml.load(f)
            if type(msg_modules) is not dict:
                raise Exception("{0}.yml format error, please check.".format(ne_type.title()))
            self._modules[ne_type.title()] = msg_modules
        return msg_modules