# coding=utf-8
import time
from testlib.infrastructure.utility import ThreadLogger
from testlib.infrastructure.utility.DictUtility import DictUtility


class MessageBuffer(object):

    def __init__(self):
        self._messages = []

    def add_message(self, msg):
        self._messages.extend(msg)

    def wait_message(self, msg_type, condition, check_sequence=True, wait_time=10, expect=True):
        repeat_times = wait_time * 10
        while repeat_times + 1:
            ThreadLogger.write_cached_log()
            msg = self._get_received_message(msg_type, condition, check_sequence)
            if msg is not None:
                ThreadLogger.write_cached_log()
                if expect:
                    return msg
                else:
                    raise Exception("Receive Unexpect message msg_type[{0}] condition[{1}] ".format(msg_type, condition))
            repeat_times -= 1
            time.sleep(0.1)
        if expect:
            raise Exception("Receive message time out, msg_type[{0}] condition[{1}] ".format(msg_type, condition))

    def _get_received_message(self, msg_type, condition, check_sequence=True):
        temp_list = []
        for msg in self._messages:
            if DictUtility.is_sub_dict(msg, condition):
                temp_list.append(msg)
                self._remove_msg_in_messages(temp_list)
                return msg
            elif check_sequence:
                temp_list.append(msg)
            else:
                continue

        self._remove_msg_in_messages(temp_list)
        return None

    def _remove_msg_in_messages(self, temp_list):
        if len(temp_list) == 0:
            return
        for msg in temp_list:
            if msg in self._messages:
                self._messages.remove(msg)
