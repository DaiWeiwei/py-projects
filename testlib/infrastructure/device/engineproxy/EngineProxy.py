# coding=utf-8
import threading
import struct
import time
import json

from MsgQueue import *
from testlib.infrastructure.channels.tcp.Tcp import Tcp
from testlib.infrastructure.utility import ThreadLogger
from testlib.domain.ne.NeRepository import NeRepository
#from testlib.infrastructure.utility.Singleton import Singleton


#@Singleton
class EngineProxy(object):
    def __init__(self, ip, port, timeout=5):
        self.__host = ip
        self.__port = port
        self.__msgQueue = MsgQueue()
        self.__channel = Tcp(self.__host, self.__port, timeout=timeout)
        self._connect()
        self._start_receive_thread()
        self._start_dispatcher_thread()

    def __del__(self):
        try:
            self.__channel.disconnect()
            self.__receive_thread.join(1)
            self.__msg_dispatcher_thread.join(1)
        except:
            pass

    def _start_receive_thread(self):
        self.__receive_thread = threading.Thread(
            target=self._socket_receive)
        self.__receive_thread.daemon = True
        self.__receive_thread.start()

    def _start_dispatcher_thread(self):
        self.__msg_dispatcher_thread = threading.Thread(
            name='EngineReceiveThread', target=self._message_dispatcher_loop)
        self.__msg_dispatcher_thread.daemon = True
        self.__msg_dispatcher_thread.start()

    def _connect(self):
        self.__channel.connect()

    def _socket_send(self, data):
        data_length = struct.pack("!l", len(data))
        #send_data = str(data_length + data)
        send_data = data_length + data
        try:
            self.__channel.write(send_data)
        except:
            raise Exception

    def _socket_receive(self):
        receive_data = ''
        while True:
            time.sleep(0.01)
            read_buff = self.__channel.read()
            if not read_buff:
                continue
            receive_data += read_buff
            while True:
                if len(receive_data) < 4:
                    break
                data_length = int(struct.unpack('!l', receive_data[:4])[0])
                if len(receive_data) - 4 >= data_length:
                    msg_data = receive_data[4:4 + data_length]
                    self.__msgQueue.add_msg(msg_data)
                    receive_data = receive_data[4 + data_length:]
                else:
                    break

    def send_msg(self, msg):
        _send_msg = json.dumps(msg)
        _send_msg = str(_send_msg)
        self._socket_send(_send_msg)

    def _message_dispatcher_loop(self):
        while True:
            msg = self.__msgQueue.get_msg()
            if msg:
                self._message_dispatcher(msg)
            # else:
            #     time.sleep(0.001)

    def _message_dispatcher(self, str_msg):
        try:
            msg = json.loads(str_msg)
        except:
            ThreadLogger.cache_log("json.loads(%s) Fail" % str_msg, "WARN")
            return
        if "type" in msg and msg["type"] == "log":
            self._print_engine_log(msg["message"], msg["level"])
            return
        id = msg["id"]
        ne = NeRepository().find(id)
        if not ne:
            ThreadLogger.cache_log("cannot find ne=%s, error" % id, "WARN")
            return
        ne.append_receive_message(msg)

    def is_connect_server_success(self):
        return self.__channel.is_connected()

    @staticmethod
    def _print_engine_log(engine_log, level):
        print_level = {"0": "ERROR",
                       "1": "INFO",
                       "2": "TRACE",
                       "3": "TRACE"
                       }
        ThreadLogger.cache_log('Engine : {0}'.format(engine_log), print_level.get(level, 'INFO'))


def create_pstt_engine_proxy(ip,port,name):
    pstt = NeRepository.find(name)
    if not pstt:
       pstt =  EngineProxy(ip,port)
       NeRepository.add(pstt)