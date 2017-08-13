#coding=utf-8
import os
from testlib.infrastructure.resource.resource.adapter import yaml
from testlib.infrastructure.utility.Singleton import Singleton


@Singleton
class InitModule(object):

    def __init__(self):
        self._modules = {}

    @property
    def modules(self):
        return self._modules

    def get(self, ne_type):
        init_txt = self._modules.get(ne_type)
        if init_txt is None:
            with open(os.path.dirname(__file__) +
                     '/initalfile/'+ne_type.title()+'.yml') as f:
                init_txt = f.read()
                self._modules[ne_type.title()] = init_txt
        init_module = yaml.load(init_txt)
        if type(init_module) is not dict:
            raise Exception(
                "{0}.yml format error, please check.".format(ne_type.title()))
        return init_module