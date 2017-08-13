# coding=utf-8

from EngineProxy import EngineProxy
from testlib.infrastructure.device.DeviceRepository import DeviceRepository


class EngineProxyCreator(object):
    @staticmethod
    def create_engine_proxy(server, port, alias):
        proxy = DeviceRepository().find(alias)
        if proxy is not None:
            return proxy
        proxy = EngineProxy(server, port)
        DeviceRepository().add(alias, proxy)
        return proxy

    @staticmethod
    def delete_engine_proxy(alias):
        proxy = DeviceRepository().find(alias)
        if proxy is not None:
            DeviceRepository().delete(alias)
            del proxy

    @staticmethod
    def find_engine_proxy(alias):
        return DeviceRepository().find(alias)

