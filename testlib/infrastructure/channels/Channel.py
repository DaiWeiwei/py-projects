# coding=utf-8


class Channel(object):
    def __init__(self, host, port,flag = "", name='channel'):
        self._tn = None
        self._name = name
        self._host = host
        self._port = port
        self._flag = flag
        self._id = self._name + self._host + str(self._port) + str(self._flag)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def get_id(self):
        return self._id

    def read(self):
        raise NotImplementedError("read must be implemented!")

    def write(self, data):
        raise NotImplementedError("write must be implemented!")

    def connect(self, *args):
        raise NotImplementedError("connect must be implemented!")

    def disconnect(self, *args):
        raise NotImplementedError("disconnect must be implemented!")

    def is_connected(self, *args):
        raise NotImplementedError("is_connect must be implemented!")