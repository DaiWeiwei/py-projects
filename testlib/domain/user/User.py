# coding=utf-8
from robot.api import logger
from testlib.infrastructure.utility.ObjectChecking import ObjectChecking
from testlib.infrastructure.utility.SnGenerator import SnGenerator
from testlib.domain.ne.NeRepository import NeRepository


class User(object):
    _unique_id_generator = SnGenerator()

    def __init__(self, user_alias):
        if not ObjectChecking().is_valid_ailas(user_alias):
            raise Exception('user_alias = {0} should be string and not empty'.format(user_alias))

        super(User, self).__init__()
        self._id = self._unique_id_generator.get()  # 全局唯一用户ID
        self.alias = user_alias
        self.imsi = PhoneBookOperate().get_id(user_alias, 'imsi')
        self.imei = PhoneBookOperate().get_id(user_alias, 'imei')

        self._mme_user = MmeUser(self)
        self._pcrf_user = PcrfUser(self)
        self._ocs_user = OcsUser(self)
        self._Cdr_user = CdrUser(self)
        self._sgsn_user = SgsnUser(self)
        self._rnc_user = RncUser(self)
        self._sgw_user = SgwUser(self)
        self.new_media = False

    @property
    def id(self):
        return self._id

    def role(self, ne_type_name):
        return Role.convert(self, ne_type_name + "User")

    def _user_role(self, ne_alias, ne_type):
        """ 获取用户角色
        :param ne_alias: 用户所在网元别名，或者用户角色如“Mme”
        :param ne_type: 如果ne_alias不带，则此参数必带，用于获取用户角色
        """
        if ne_alias is None and ne_type is None:
            raise Exception("The user's src_ne is not specified.")
        if ne_alias:
            ne = NeRepository().find(ne_alias)
            if ne is None:
                raise Exception("The ne({0}) does not exist. please check EnvironmentRequirements.py".format(ne_alias))
            return self.role(ne.type)
        return self.role(ne_type)

    def front_ne_role(self, ne_alias=None, ne_type=None):
        if ne_alias or ne_type:
            return self._user_role(ne_alias, ne_type)
        # todo: 后续增加SGW等前向网元时，需要在这里增加。
        if not self._mme_user.have_no_session() and not self._sgsn_user.have_no_session() and not self._sgw_user.have_no_session():
            raise Exception("User in multi ne, Please specify the src_ne.")
        if not self._mme_user.have_no_session():
            return self._mme_user
        if not self._sgsn_user.have_no_session():
            return self._sgsn_user
        if not self._sgw_user.have_no_session():
            return self._sgw_user
        raise Exception("User is not attached, Please check or specify the src_ne.")

    def release(self):
        self._mme_user.check_no_expect_left()
        self._pcrf_user.check_no_expect_left()
        self._ocs_user.check_no_expect_left()
        self._Cdr_user.check_no_expect_left()
        self._sgsn_user.check_no_expect_left()
        self._rnc_user.check_no_expect_left()
        # todo: 后续增加SGW等前向网元时，需要在这里增加。
        self.role("Mme").release_resource()
        self.role("Sgsn").release_resource()
        self.role("Sgw").release_resource()

    def send(self, msg_type, session_alias, bear_alias, src, opposite=None, ne_type=None, delay=None):
        logger.trace('User send %s, %s, %s, %s. ' % (msg_type, self.alias, session_alias, bear_alias))
        user_role = self._user_role(src, ne_type)
        user_role.send(msg_type, session_alias, bear_alias, src, opposite, delay)

    def receive(self, msg_type, session_alias, bear_alias, src, opposite=None, ne_type=None,
                check_sequence=True, wait_time=10, expect=True):
        logger.trace('User wait %s, %s, %s, %s. ' % (msg_type, self.alias, session_alias, bear_alias))
        user_role = self._user_role(src, ne_type)
        user_role.receive(msg_type, session_alias, bear_alias, src, opposite, check_sequence, wait_time, expect)

    def send_traffic(self, msg_type, session_alias, bear_alias, pdn_alias, bearip, src, opposite=None, data_length=64):
        user_role = self.front_ne_role(src)
        user_role.send_traffic(msg_type, session_alias, bear_alias, pdn_alias, bearip, src, opposite, data_length)

    def receive_traffic(self, msg_type, session_alias, bear_alias, pdn_alias, src=None, wait_time=10, expect=True):
        user_role = self.front_ne_role(src)
        user_role.receive_traffic(msg_type, session_alias, bear_alias, pdn_alias, wait_time, expect)

    def send_capfile(self, msg_type, session_alias, bear_alias, filename, file_pdn_addr, bearip, packet_interval,
                     src, opposite=None, pdn=None, pgw=None):
        user_role = self.front_ne_role(src)
        user_role.send_capfile(msg_type, session_alias, bear_alias, filename, file_pdn_addr, bearip, packet_interval,
                               src, opposite, pdn, pgw)

    def send_auto_media(self, msg_type, session_alias, bear_alias, profile_name, src, opposite=None):
        user_role = self.front_ne_role(src)
        user_role.send_auto_media(msg_type, session_alias, bear_alias, profile_name, src, opposite)

    def send_traffic_ex(self, msg_type, session_alias, bear_alias, pdn_alias, bearip, src, opposite=None,
                        data_length=64):
        user_role = self.front_ne_role(src)
        user_role.send_traffic_ex(msg_type, session_alias, bear_alias, pdn_alias, bearip, src, opposite, data_length)

    def receive_traffic_ex(self, msg_type, session_alias, bear_alias, src=None, check_sequence=True, wait_time=10,
                           expect=True):
        user_role = self.front_ne_role(src)
        user_role.receive_traffic_ex(msg_type, session_alias, bear_alias, wait_time, check_sequence, expect)



