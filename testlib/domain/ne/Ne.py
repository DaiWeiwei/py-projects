# coding=utf-8


class Ne(object):

    def __init__(self, _id, ip, _type):
        self._id = _id
        self._ip = ip
        self._type = _type.title()
        self._linkNeList = []

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def short_id(self):
        return self._id.rstrip("_simu")

    @property
    def ip(self):
        return self._ip

    def release_user_resource(self):
        # 网元释放资源需要在各子类实现， 模拟网元可能释放用户会话等索引资源， 真实网元可能其他
        pass
