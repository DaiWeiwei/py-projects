# coding=utf-8
import logging
import socket
from testlib.infrastructure.channels.Channel import Channel


class Tcp(Channel):
    def __init__(self, host, port,flag = "", timeout=5):
        super(Tcp, self).__init__(host, port,flag)
        self._timeout = timeout
        self._buf_size = 1024

    def __del__(self):
        if self._tn is not None:
            self._tn.close()
            self._tn = None

    def connect(self, *args):
        addr = (self._host, int(self._port))
        try:
            self._tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tn.settimeout(self._timeout)
            logging.info("connect to %s" % (addr,))
            self._tn.connect(addr)
        except socket.error, e:
            self.disconnect()
            raise Exception("create tcp link to {0} failed, error:{1}.".format(addr, e))
        else:
            return self._tn

    def disconnect(self, *args):
        try:
            if self._tn is not None:
                self._tn.close()
        except socket.error, e:
            logging.error("close tcp link failed, error:{0}".format(e))
        finally:
            self._tn = None

    def read(self):
        if self._tn is None:
            logging.error('tcp link is not create')
        else:
            try:
                data = ''
                data = self._tn.recv(self._buf_size)
            except AttributeError, e0:
                logging.error('tcp read: {0}'.format(e0))
            except socket.timeout, e1:
                logging.warn('tcp read : {0}'.format(e1))
            except socket.error, e2:
                logging.info('tcp read : {0}'.format(e2))
            else:
                return data

    def write(self, data):
        if self._tn is None:
            logging.error('tcp link is not create')
        else:
            try:
                self._tn.sendall(data)
            except AttributeError, e0:
                logging.error('tcp write : {0}'.format(e0))
            except socket.error, e1:
                logging.error('tcp write error : {0}'.format(e1))
            except Exception, e2:
                logging.error('tcp write error : {0}'.format(e2))

    def get_status(self):
        return self._tn is not None
