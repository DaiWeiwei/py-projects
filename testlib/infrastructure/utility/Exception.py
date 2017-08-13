# coding=utf-8


class NeNotFoundException(Exception):

    def __init__(self, ne_name):
        self._ne_name = ne_name

    def __str__(self):
        return "The ne {0} isn't exist".format(self._ne_name)


class LinkNotFoundException(Exception):

    def __init__(self, from_ne, to_ne):
        self._from_ne = from_ne
        self._to_ne = to_ne

    def __str__(self):
        return "The link from {0} to {1} isn't exist"\
            .format(self._from_ne, self._to_ne)


class MessageParamNotFoundException(Exception):

    def __init__(self, message, param_path):
        self._message = message
        self._param_path = param_path

    def __str__(self):
        return "Key {0} in message {1} isn't existed"\
            .format(self._param_path, self._message.name)


class MessageCheckException(Exception):

    def __init__(self, actual, expect, path=None):
        self._actual = actual
        self._expect = expect
        self._path = path

    def __str__(self):
        if self._path:
            return "Check key {0} failed, actual is {1}, expect is {2}"\
                .format(self._path, self._actual, self._expect)
        else:
            return "Check failed, actual is {1}, expect is {2}"\
                .format(self._actual, self._expect)

class SocketException(Exception):
    pass