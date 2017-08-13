# coding=utf-8
from testlib.infrastructure.utility.ObjectRepository import ObjectRepository
from testlib.infrastructure.utility.Singleton import Singleton


@Singleton
class ConfigRepository(ObjectRepository):
    def __init__(self):
        ObjectRepository.__init__(self)