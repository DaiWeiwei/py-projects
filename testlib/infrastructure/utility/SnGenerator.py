# encoding = utf-8
import random


class SnGenerator(object):
    """
    Generate a serial number based on input number*1000000 increase progressively
    return: base_num*1000000 + sequence
    """

    def __init__(self, base_number=None, max_number=0xFFFFFFFF):
        if base_number is None:
            base_number = random.randrange(100, 999) * 10000
        if base_number > max_number:
            base_number = base_number % max_number
        self._number = base_number
        self._max_number = max_number

    def get(self):
        self._number += 1
        if self._number > self._max_number:
            self._number = 1
        return self._number
