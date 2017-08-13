# coding=utf-8
import logging
import socket
import telnetlib
import time
import re
from testlib.infrastructure.channels.Channel import Channel
from testlib.infrastructure.utility.Exception import SocketException
from telnetlib import WILL, DO, NAWS, IAC, DONT, BINARY, SE, SB


class Telnet(Channel):
    '''
    Telnet
    '''

    def __init__(self, host, port, flag="", timeout=5):
        '''
        Constructor
        '''
        super(Telnet, self).__init__(host, port, flag)
        self._timeout = timeout
        self.matchIndex = -1
        self.pagebreak = ''
        self.prompt = '#'

    def _read_expect_str(self, cmd_obj):
        expect_list = [cmd_obj.expected]
        tp = self._expect(expect_list, cmd_obj.timeout)
        # tp = self._tn.expect(expect_list, cmd_obj.timeout)
        if tp[0] < 0:
            raise Exception('cannot find expected "{0}" from received "{1}"'.format(cmd_obj.expected, tp[2]))
        cmd_obj.success_to_excute(tp[2])
        self.matchIndex = tp[0]
        return cmd_obj

    def _read_expect_list(self, cmd_obj):
        tp = self._tn.expect(cmd_obj.expected, cmd_obj.timeout)
        cmd_obj.success_to_excute(tp[2])
        self.matchIndex = tp[0]
        return cmd_obj

    def read(self, cmd_obj, try_times=10):
        while try_times >= 0:
            try:
                return self._read(cmd_obj)
            except SocketException, e:
                try_times -= 1
                if try_times == 0:
                    raise e

            except:
                break

    def _read(self, cmd_obj):
        if self._tn is None:
            logging.error('Telnet tunnel is not exists, please check it!')
            cmd_obj.fail_to_excute('Telnet is not exists, please check it!')
        else:
            try:
                if isinstance(cmd_obj.expected, (str)):
                    self._read_expect_str(cmd_obj)
                elif isinstance(cmd_obj.expected, (list)):
                    self._read_expect_list(cmd_obj)
                else:
                    logging.error('cmd_obj.expected shoule be str or list')
                    cmd_obj.fail_to_excute('cmd_obj.expected shoule be str or list')
                    self.matchIndex = -1
            except AttributeError, e1:
                raise Exception('Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e1))
                # cmd_obj.fail_to_excute('Telnet通道异常, err={0}'.format(e1))
            except socket.error, e2:
                raise SocketException(
                    'Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e2))
                # cmd_obj.fail_to_excute('Telnet通道异常, err={0}'.format(e2))
            except EOFError, e3:
                raise Exception('Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e3))
                # cmd_obj.fail_to_excute('Telnet通道异常, err={0}'.format(e3))
            except Exception, e4:
                raise Exception('Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e4))
                # cmd_obj.fail_to_excute('Telnet校验失败, err={0}'.format(e4))
            return cmd_obj

    def write(self, cmd_obj, try_times=10):
        while try_times >= 0:
            try:
                return self._write(cmd_obj)
            except SocketException, e:
                try_times -= 1
                if try_times == 0:
                    raise e
                time.sleep(2)
            except:
                break

    def _write(self, cmd_obj):
        if self._tn is None:
            logging.error('Telnet tunnel is not exists')
            cmd_obj.fail_to_excute('Telnet is not exists')
        else:
            try:
                self._tn.read_very_eager()
                self._tn.write('{0}\n'.format(cmd_obj.command))
            except AttributeError, e1:
                raise Exception('Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e1))
                # cmd_obj.fail_to_excute('Telnet通道异常, err={0}'.format(e1))
            except socket.error, e2:
                raise SocketException(
                    'Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e2))
                # cmd_obj.fail_to_excute('Telnet通道异常, err={0}'.format(e2))
            except EOFError, e3:
                raise Exception('Telnet tunnel(host={0},port={1}) exception, err={2}'.format(self.host, self.port, e3))
                # cmd_obj.fail_to_excute('Telnet通道异常, err={0}'.format(e3))
        return cmd_obj

    def connect(self, *args):
        try:
            # logging.info('Telnet ip:{0},port:{1},time:{2}'.format(self._host, self._port, self._timeout))
            self._tn = telnetlib.Telnet(self._host, self._port, self._timeout)
            self._tn.set_option_negotiation_callback(Telnet._option_negotiation)
        except socket.error, e1:
            self.disconnect()
            raise Exception('Telnet can not be create, please check the param or '
                            'network status! err=%s' % (e1))
        else:
            # self._tn.open(self.address, self.port, self._timeout)
            return self._tn

    def disconnect(self, *args):
        if self._tn is not None:
            try:
                self._tn.close()
            except:
                pass
        self._tn = None

    def is_connected(self):
        try:
            self._tn.write("\n")
        except:
            return False
        return True

    def excute_cmd(self, cmd_obj):
        if cmd_obj.command is not None:
            cmd_obj = self.write(cmd_obj)
        if cmd_obj.expected is not None and cmd_obj.cmd_result.result:
            cmd_obj = self.read(cmd_obj)
        return cmd_obj.cmd_result

    @staticmethod
    def _compile_expect_list(_expect_list):
        list_num = len(_expect_list)
        compiled_expect_list = [None] * list_num
        for index in range(list_num):
            compiled_expect_list[index] = re.compile(_expect_list[index])
        return compiled_expect_list

    @staticmethod
    def _match_expect(compiled_expect_list, match_string):
        list_num = len(compiled_expect_list)
        for index in range(list_num):
            m = compiled_expect_list[index].search(match_string)
            if m:
                return index, m, match_string[:m.end()]
        return -1, None, match_string

    def _telnet_expect(self, _expect_list, timeout=None):
        compiled_expect_list = Telnet._compile_expect_list(_expect_list)
        receive_data = ''
        tp = None
        if timeout is not None:
            time_start = time.time()
        while True:
            time.sleep(0.05)
            receive_data += self._tn.read_very_eager()
            tp = Telnet._match_expect(compiled_expect_list, receive_data)
            if tp[0] >= 0:
                if receive_data.endswith(self.pagebreak):
                    self._tn.write('a')
                break
            if receive_data.endswith(self.pagebreak):
                self._tn.write('\x20')
            if timeout is not None:
                elapsed = time.time() - time_start
                if elapsed >= timeout:
                    break
        return tp

    def _expect(self, _expect_list, timeout=None):
        return self._telnet_expect(_expect_list, timeout)

    def _has_page_break(self):
        return len(self.pagebreak) > 0

    @staticmethod
    def _option_negotiation(sock, cmd, opt):
        if cmd in [WILL, DO]:
            if opt == NAWS:
                sock.sendall(IAC + WILL + opt +
                             IAC + SB + opt +
                             BINARY + chr(254) +
                             BINARY + chr(254) +
                             IAC + SE)
            else:
                sock.sendall(IAC + DONT + opt)


if __name__ == '__main__':
    pass
