# coding=utf-8
from robot.api import logger
from testlib.domain.ne.NeRepository import NeRepository
from testlib.infrastructure.utility.CommDataArea import CommDataArea
from testlib.infrastructure.utility.ObjectRepository import ObjectRepository
from testlib.infrastructure.message.MessageBuffer import MessageBuffer
from testlib.domain.session.Session import Session
from testlib.infrastructure.message.Message import Message
from testlib.infrastructure.message.MessageModule import *
from testlib.infrastructure.utility.DictUtility import DictUtility
from robot.libraries.BuiltIn import BuiltIn


class UserRole(object):
    def __init__(self, user):
        self.user = user
        self._full_name = self.__class__.__name__ + "." + user.alias
        self._data_area = CommDataArea(self._full_name)
        self._sessions = ObjectRepository()
        self._messages = MessageBuffer()
        self._send_msgs = []
        self._bear_ids = []

    def __del__(self):
        for _, session in self._sessions.items():
            self.delete_session(session.alias)

    def __getattr__(self, item):
        try:
            return getattr(self._data_area, item)
        except:
            return getattr(self._messages, item)

    @property
    def full_name(self):
        return self._full_name

    def cache_send_msg(self, msg):
        self._send_msgs.append(msg)

    def has_send_cache(self):
        return len(self._send_msgs) > 0

    def cached_send_msg(self):
        return self._send_msgs

    def reset_send_msg(self):
        self._send_msgs = []

    def check_no_expect_left(self):
        self._data_area.check_no_expect_left()
        for _, session in self._sessions.items():
            session.check_no_expect_left()

    def release_resource(self):
        pass
        # raise NotImplementedError   # 各子类实现各自角色用户资源的释放

    def have_no_session(self):
        return self._sessions.is_empty()

    def create_session(self, session_alias):
        session = Session(session_alias, self)
        self.init_session(session)
        self._sessions.add(session_alias, session)
        return session

    def init_session(self, session):
        pass

    def init_bear(self, session):
        pass

    @staticmethod
    def update_session_field_related_to_ne(session):
        pass

    def delete_session(self, session_alias):
        session = self._sessions.find(session_alias)
        if session is not None:
            # if session.ne is not None and session.ne.sessions is not None:
            # session.ne.delete_session(session.ne.sessions.session_id)
            self._sessions.delete(session_alias)

    def get_session(self, session_alias):
        session = self._sessions.find(session_alias)
        if session is None:
            session = self.create_session(session_alias)
        return session

    def have_sequence_number(self, sequence_number):
        for _, session in self._sessions.items():
            if session.msg_sequence_number == sequence_number:
                return True
        return False

    def _allocate_bear_id(self):
        for i in range(5, 10000):
            if i in self._bear_ids:
                continue
            self._bear_ids.append(i)
            return i

    def deallocate_bear_id(self, bear_id):
        self._bear_ids.remove(bear_id)

    def modify_bear_id(self, old_bear_id, new_bear_id):
        if old_bear_id == new_bear_id:
            return
        if new_bear_id in self._bear_ids:
            raise Exception("modify_bear_id:bear_id[{0}] already in use, please change it.".format(new_bear_id))
        self._bear_ids.remove(old_bear_id)
        self._bear_ids.append(new_bear_id)

    def create_bear(self, session, bear_alias):
        bear_id = self._allocate_bear_id()
        bear = session.create_bear(bear_alias, bear_id)
        self.init_bear(bear)
        return bear

    def get_bear(self, session_alias, bear_alias):
        session = self.get_session(session_alias)
        bear = session.find_bear(bear_alias)
        if bear is None:
            bear = self.create_bear(session, bear_alias)
        return bear

    def set_fields(self, key_values, msg_type=None, serial_number=1):
        for key, value in key_values.items():
            self.set_field(key, value, msg_type, serial_number)

    def set_field_in_session(self, session_alias, key, value, msg_type=None, serial_number=None):
        session = self.get_session(session_alias)
        session.set_field(key, value, msg_type, serial_number)

    def set_fields_in_session(self, session_alias, key_values, msg_type=None, serial_number=None):
        for key, value in key_values.items():
            self.set_field_in_session(session_alias, key, value, msg_type, serial_number)

    def set_condition_field_in_session(self, session_alias, key, value, msg_type=None, serial_number=1):
        session = self.get_session(session_alias)
        session.set_condition_field(msg_type, key, value, serial_number)

    def set_condition_field_in_bear(self, session_alias, bear_alias, key, value, msg_type=None, serial_number=1):
        bear = self.get_bear(session_alias, bear_alias)
        bear.set_condition_field(msg_type, key, value, serial_number)

    # todo clear_field_in_bear待删除
    def clear_field_in_bear(self, session_alias, bear_alias, key):
        bear = self.get_bear(session_alias, bear_alias)
        bear.clear_field(key)

    def get_field_in_session(self, session_alias, key, default=None, msg_type=None, serial_number=None):
        session = self.get_session(session_alias)
        return session.get_field(key, default, msg_type, serial_number)

    def get_set_field_in_session(self, session_alias, key, default=None, msg_type=None, serial_number=None):
        session = self.get_session(session_alias)
        return session.get_set_field(key, default, msg_type, serial_number)

    def get_field_in_bear(self, session_alias, bear_alias, key, default=None, msg_type=None, serial_number=None):
        bear = self.get_bear(session_alias, bear_alias)
        return bear.get_field(key, default, msg_type, serial_number)

    def get_set_field_in_bear(self, session_alias, bear_alias, key, default=None, msg_type=None, serial_number=None):
        bear = self.get_bear(session_alias, bear_alias)
        return bear.get_set_field(key, default, msg_type, serial_number)

    def get_expect_in_session(self, session_alias, msg_type, key, default=None, serial_number=1):
        session = self.get_session(session_alias)
        return session.get_expect_field(msg_type, key, default, serial_number)

    def set_expect_in_session(self, session_alias, msg_type, key, value, serial_number=1):
        session = self.get_session(session_alias)
        session.set_expect_field(msg_type, key, value, serial_number)

    def set_field_in_bear(self, session_alias, bear_alias, key, value, msg_type=None, serial_number=None):
        bear = self.get_bear(session_alias, bear_alias)
        bear.set_field(key, value, msg_type, serial_number)

    def update_field_in_bear(self, session_alias, bear_alias, key, value, msg_type=None, serial_number=1):
        bear = self.get_bear(session_alias, bear_alias)
        bear.update_field(key, value, msg_type, serial_number)

    def set_fields_in_bear(self, session_alias, bear_alias, key_values, msg_type=None, serial_number=1):
        for key, value in key_values.items():
            self.set_field_in_bear(session_alias, bear_alias, key, value, msg_type, serial_number)

    def update_fields_in_bear(self, session_alias, bear_alias, key_values, msg_type=None, serial_number=1):
        for key, value in key_values.items():
            self.update_field_in_bear(session_alias, bear_alias, key, value, msg_type, serial_number)

    def set_expect_in_bear(self, session_alias, bear_alias, msg_type, key, value, serial_number=1):
        bear = self.get_bear(session_alias, bear_alias)
        bear.set_expect_field(msg_type, key, value, serial_number)

    def get_expect_in_bear(self, session_alias, bear_alias, msg_type, key, default=None, serial_number=1):
        bear = self.get_bear(session_alias, bear_alias)
        return bear.get_expect_field(msg_type, key, default, serial_number)

    def set_expect_fields_in_bear(self, session_alias, bear_alias, msg_type, key_values, serial_number=1):
        for key, value in key_values.items():
            self.set_expect_in_bear(session_alias, bear_alias, msg_type, key, value, serial_number)

    def init_session_ne(self, session_alias, src, opposite):
        session = self.get_session(session_alias)
        if ((session.ne and session.opposite_ne) and
                (src is None or session.ne.id == src) and
                (opposite is None or session.opposite_ne.id == opposite)):
            return session

        if src is not None:
            ne = NeRepository().find(src)
            session.ne = ne

        if opposite is not None:
            opposite_ne = NeRepository().find(opposite)
            session.set_opposite_ne(opposite_ne)

        if session.ne is None or session.opposite_ne is None:
            raise Exception("The src_ne and opposite_ne is not specified, src={0} opposite={1}".format(src, opposite))
        session.set_link(session.ne.id, session.opposite_ne.id)
        self.update_session_field_related_to_ne(session)
        return session

    def send_cached_msgs(self, ne, msg):
        self.cache_send_msg(msg)
        msgs = self.cached_send_msg()
        ne.send_msg(msgs)
        self.reset_send_msg()

    def send(self, msg_type, session_alias, bear_alias=None, src=None, opposite=None, delay=None):
        session = self.get_session(session_alias)
        self.init_session_ne(session_alias, src, opposite)
        session.set_sequence_number(session.ne.generate_sequence_number())
        session.ne.add_user(self.user)
        session.ne.add_session(session)

        msg = self.encode_msg(msg_type, session, bear_alias)
        if delay:
            self.cache_send_msg(msg)
        else:
            if self.has_send_cache():
                self.send_cached_msgs(session.ne, msg)
            else:
                session.ne.send_msg(msg)
        self.state_switching_after_send_msg(msg_type, session, bear_alias)

    def encode_msg(self, msg_type, session, bear_alias):
        pass  # 子类实现

    def state_switching_after_send_msg(self, msg_type, session, bear_alias):
        pass  # 子类实现

    def receive(self, msg_type, session_alias, bear_alias=None, src=None, opposite=None,
                check_sequence=True, wait_time=10, expect=True):
        session = self.get_session(session_alias)
        self.init_session_ne(session_alias, src, opposite)

        condition = self.get_condition(msg_type, session, bear_alias, expect)
        msg = self.wait_message(msg_type, condition, check_sequence, wait_time, expect)
        if not expect:
            return
        self._check_msg_deal(msg, session)
        self.receive_msg_deal(msg, session, bear_alias)

    def get_condition(self, msg_type, session, bear_alias, expect=True):
        msg_module = session.ne.msg_modules.get(msg_type)
        if bear_alias and type(bear_alias) is not list:
            bear = self.get_bear(session.alias, bear_alias)
        else:
            bear = None
        condition = self._get_matched_condition(msg_module, session, bear)
        DictUtility.update_dict(condition, session.get_condition_fields(msg_type))
        if bear is not None:
            DictUtility.update_dict(condition, bear.get_condition_fields(msg_type))
        if not expect:
            DictUtility.update_dict(condition, self._get_unexpect_condition(msg_type, session, bear))
        logger.debug("{0:13} {1:8} {2:20} {3:19} {4}".format(
            self._short_name, "wait", msg_type, 'Condition:', condition))
        return condition

    def _get_matched_condition(self, msg_module, session, bear):
        if RECEIVE_CONDITION in msg_module.keys():
            return self._get_condition_by_mode(msg_module[RECEIVE_CONDITION], session, bear)
        if COMMON_RECEIVE_CONDITION in session.ne.msg_modules.keys():
            return self._get_condition_by_mode(session.ne.msg_modules[COMMON_RECEIVE_CONDITION], session, bear)
        return {}

    @staticmethod
    def _get_condition_by_mode(condition_info, session, bear):
        compound_condition = {}
        for (condition_type, condition_mode) in condition_info.items():
            condition = {}
            if condition_type == FIX:
                condition = condition_mode
            if condition_type == SESSION:
                session.fill_condition(condition, condition_mode)
            if condition_type == BEAR:
                if bear is not None:
                    bear.fill_condition(condition, condition_mode)
            DictUtility.update_dict(compound_condition, condition)
        return compound_condition

    def _get_unexpect_condition(self, msg_type, session, bear):
        condition = {}
        DictUtility.update_dict(condition, self.get_expect_fields(msg_type))
        DictUtility.update_dict(condition, session.get_expect_fields(msg_type))
        if bear is not None:
            DictUtility.update_dict(condition, bear.get_expect_fields(msg_type))
        return condition

    def _check_msg_deal(self, msg, session):
        self.check_expect(msg)
        session.check_expect(msg)

    @staticmethod
    def _get_real_expect_field(msg_module, sub_fields):
        parameter_struct_name = msg_module.get(PARAMETER_STRUCT_NAME)
        if parameter_struct_name is None:
            return sub_fields
        return {parameter_struct_name: sub_fields} if sub_fields else {}

    def receive_msg_deal(self, msg, session, bear_alias):
        self.receive_msg_deal_user(msg)
        self.receive_msg_deal_session(msg, session)
        self.receive_msg_deal_bear(msg, session, bear_alias)
        self.special_deal_after_receive_msg(msg, session, bear_alias)

    def special_deal_after_receive_msg(self, msg, session, bear_alias):
        pass  # 子类实现

    def receive_msg_deal_user(self, msg):
        self.save_field_from_msg(msg, module=msg.module.get(USER))

    def receive_msg_deal_session(self, msg, session):
        session_module = msg.module.get(SESSION)
        if session_module is None:
            return
        deal_type = self._get_domain_dealtype(session_module)
        if not deal_type:
            session.save_field_from_msg(msg, module=session_module)
        else:
            session.save_field_from_msg(msg, module=session_module.get(deal_type[0]))
        self.session_state_switching(msg, session)

    def _get_domain_dealtype(self, domain_module):
        deal_type = []
        for deal_type_name in [DEAL_CREATE, DEAL_REMOVE, DEAL_MODIFY]:
            if deal_type_name in domain_module:
                deal_type.append(deal_type_name)
        return deal_type

    def session_state_switching(self, msg, session):
        # logger.trace('receive msg,deal session,session state switching beg')
        session_module = msg.module.get(SESSION)
        deal_types = self._get_domain_dealtype(session_module)
        if not deal_types:
            logger.debug('receive msg,deal session,session state switching ,deal type is None')
            return
        deal_type = deal_types[0]
        if msg.is_response():
            # 接收响应消息
            if msg.is_fail():
                return
            if deal_type == DEAL_CREATE:
                self.session_state_switching_by_create_res(session)
            elif deal_type == DEAL_REMOVE:
                self.session_state_switching_by_remove_res(session)
        else:  # 接收请求消息
            session_id = self.get_session_id_from_req(msg, session_module)
            if session_id is None:
                logger.debug('receive msg,deal session,receive req,but session_id is None')
                return
            if deal_type == DEAL_CREATE:
                self.session_state_switching_by_create_req(session_id, session)
            elif deal_type == DEAL_REMOVE:
                self.session_state_switching_by_remove_req(session_id, session)
        # logger.trace('receive msg,deal session,session state switching end')

    def session_state_switching_by_create_res(self, session):
        session.set_established()

    def session_state_switching_by_remove_res(self, session):
        session.set_released()

    def session_state_switching_by_create_req(self, session_id, session):
        session.ne.add_session(session, session_id)

    def session_state_switching_by_remove_req(self, session_id, session):
        session.ne.delete_session(session_id)
        logger.debug('{0:8} {1:20} {2}.'.format('Receive', 'remove_request', 'delete session'))

    def get_session_id_from_req(self, msg, session_module):
        deal_type = self._get_domain_dealtype(session_module)
        if not deal_type:
            id_code = session_module.get(ID_CODE)
        else:
            id_code = session_module.get(deal_type[0]).get(ID_CODE)
        if id_code is None:
            logger.debug('receive msg,get session id from req,but id_code is None')
            return None
        session_id = DictUtility.get_field(msg.parameters, id_code)
        return session_id

    def receive_msg_deal_bear(self, msg, session, bear_alias):
        pass

    def send_traffic(self, msg_type, session_alias, bear_alias, pdn_alias, bearip, src, opposite, data_length=64):
        logger.trace('user send traffic %s.' % msg_type)
        session = self.get_session(session_alias)
        bear = self.get_bear(session_alias, bear_alias)
        if src is not None:
            self.init_session_ne(session_alias, src, opposite)
        pdn = NeRepository().find(pdn_alias)
        if pdn is None and msg_type != 'error_indication':
            raise Exception("pdn find fail, pdn_alias:{0}".format(pdn_alias))
        session.set_sequence_number(session.ne.generate_sequence_number())
        session.ne.add_user(self.user)

        getattr(self, "send_traffic_" + msg_type)(session, bear, pdn, bearip, data_length)

    def receive_traffic(self, msg_type, session_alias, bear_alias, pdn_alias, wait_time=10, expect=True):
        logger.trace('user wait traffic %s.' % msg_type)
        session = self.get_session(session_alias)
        bear = self.get_bear(session_alias, bear_alias)
        pdn = NeRepository().find(pdn_alias)
        if pdn is None:
            raise Exception("pdn find fail, pdn_alias:{0}".format(pdn_alias))
        getattr(self, "receive_traffic_" + msg_type)(session, bear, pdn, wait_time, expect)

    def set_need_bear_modify(self, session_alias, bear_alias):
        bear = self.get_bear(session_alias, bear_alias)
        bear.set_need_modify()

    def set_need_bear_remove(self, session_alias, bear_alias):
        bear = self.get_bear(session_alias, bear_alias)
        bear.set_need_remove()

    def set_need_bear_recreate(self, session_alias, bear_alias):
        bear = self.get_bear(session_alias, bear_alias)
        bear.set_need_recreate()

    def find_ebi_by_bear_alias(self, session_alias, bear_alias):
        bear = self.get_bear(session_alias, bear_alias)
        return bear.id

    def find_lbi(self, session_alias):
        session = self.get_session(session_alias)
        return session.id

    def find_teid_by_bear_alias(self, session_alias, bear_alias, teid_alias):
        bear = self.get_bear(session_alias, bear_alias)
        if bear is not None:
            return bear.get_field(teid_alias)
        return None

    def send_capfile(self, msg_type, session_alias, bear_alias, filename, file_pdn_addr, bearip, packet_interval,
                     src, opposite, pdn_alias, pgw_alias):
        logger.trace('user send capfile %s.' % msg_type)
        session = self.get_session(session_alias)
        bear = self.get_bear(session_alias, bear_alias)

        if src is not None:
            self.init_session_ne(session_alias, src, opposite)

        if pdn_alias is not None:
            pdn = NeRepository().find(pdn_alias)
            if pdn is None:
                raise Exception("pdn find fail, pdn_alias:{0}".format(pdn_alias))
            pdn_link = pdn.get_link(pgw_alias)
        else:
            pdn_link = None

        session.set_sequence_number(session.ne.generate_sequence_number())
        getattr(self, "send_capfile_" + msg_type)(session, bear, pdn_link, filename, file_pdn_addr, bearip,
                                                  packet_interval)

    def get_peer_gtpu_info(self, bear_type, session_alias, bear_alias):
        pass

    def get_local_teidu(self, session_alias, bear_alias):
        pass

    def get_local_gtpu_address(self, bear_type, session_alias, bear_alias):
        pass

    def get_end_user_address(self, session_alias):
        pass

    def get_mtu(self, session_alias):
        pass

    def _build_engine_bear(self, bear_type, peer_ipv4, peer_ipv6):
        if bear_type == 0:
            if peer_ipv4 is None:
                raise Exception("bear ipv4 not exist")
            return {'dstip': peer_ipv4}
        else:
            if peer_ipv6 is None:
                raise Exception("bear ipv6 not exist")
            return {'dstip': peer_ipv6}

    def _encode_gpdu_message(self, session, bear, bearip):
        gtpu_info = self.get_peer_gtpu_info(bearip, session.alias, bear.alias)
        peer_teidu = gtpu_info[0]
        engine_bear = self._build_engine_bear(int(bearip), gtpu_info[1], gtpu_info[2])
        wPeerFlbc = session.get_field("wPeerFlbc")
        wPeerTeidc  = session.get_field("dwPeerTeidc")
        msg = Message(link=session.link,
                      protocol="GTPV1",
                      message_type="GtpGPdu",
                      message_name="T_GtpuBearTx",
                      bear=engine_bear)
        msg["tGtpHdrCtrl"] = {'wSeqNum': session.msg_sequence_number, 'dwTeid': peer_teidu}
        msg["ucBearType"] = bearip
        return msg

    def _recv_gpdu_message(self, session, bear, wait_time, expect):
        local_teidu = self.get_local_teidu(session.alias, bear.alias)

        condition = {"tGtpHdrCtrl": {"dwTeid": local_teidu}}
        msg = self.wait_message("GtpGPdu", condition, True, wait_time, expect)
        if msg is not None and expect is False:
            return False
        return True

    def send_traffic_error_indication(self, session, bear, pdn=None, bearip=0, data_length=64):
        # todo 获取ip地址部分代码重复，后续消除，bearip名字是不是加type更合适
        bearip = int(bearip)
        gtpu_info = self.get_peer_gtpu_info(bearip, session.alias, bear.alias)
        engine_bear = self._build_engine_bear(bearip, gtpu_info[1], gtpu_info[2])
        msg = Message(link=session.link,
                      protocol="GTPV1",
                      message_type="GtpErrIndication",
                      message_name="T_ErrorIndTx",
                      bear=engine_bear)
        msg["tGtpHdrCtrl"] = {'wSeqNum': 0, 'dwTeid': 0}
        msg['dwTeidDataI'] = self.get_local_teidu(session.alias, bear.alias)
        msg['bGsnAddrCFlg'] = 1
        if bearip == 0:
            msg['acGsnAddrC'] = self.get_local_gtpu_address(bearip, session.alias, bear.alias)[0]
        else:
            msg['acGsnAddrC'] = self.get_local_gtpu_address(bearip, session.alias, bear.alias)[1]
        msg["ucBearType"] = bearip
        session.ne.send_msg(msg)

    def receive_traffic_error_indication(self, session, bear, pdn=None, wait_time=10, expect=True):
        condition = {"tGtpHdrCtrl": {"dwTeid": 0}}
        msg = self.wait_message("GtpErrIndication", condition)

    def get_pcap_file_name(self, filename):
        try:
            global_pcap_path = BuiltIn().get_variable_value('${global_pcap_path}','')
            if global_pcap_path != '':
                abs_filename = os.path.join(global_pcap_path,filename)
                if os.path.exists(abs_filename):
                    return abs_filename
                else:
                    return filename
            else:
                return filename
        except:
            return filename


    def _encode_v4capfile_message(self, session, pdn_link, filename, file_pdn_addr, packet_interval):
        msg = Message(link=session.link,
                      protocol="CAPFILE",
                      message_type="CapFile",
                      message_name="T_CapFileTx")
        ms_addr_group = self.get_end_user_address(session.alias)

        msg['acHostOffice'] = pdn_link
        msg['acFileName'] = self.get_pcap_file_name(filename)
        msg['acFileForWardNetAddr'] = file_pdn_addr
        msg['acUserAddr'] = ms_addr_group[0]
        msg['wSendTimeInt'] = packet_interval
        return msg

    def send_capfile_v4capfile(self, session, bear, pdn_link, filename, file_pdn_addr, bearip, packet_interval):
        msg0 = self._encode_gpdu_message(session, bear, bearip)
        msg1 = self._encode_v4capfile_message(session, pdn_link, filename, file_pdn_addr, packet_interval)
        session.ne.send_msg([msg0, msg1])

    def send_capfile_capfile_end(self, session, bear, pdn_link, filename, file_pdn_addr, bearip, packet_interval):
        msg = Message(operate_type="send message",
                      link=session.link,
                      protocol="CAPFILE",
                      message_type="CapFileEnd",
                      message_name="T_CapFileEndTx")
        session.ne.send_msg(msg)

    def _encode_v6capfile_message(self, session, pdn_link, filename, file_pdn_addr, packet_interval):
        msg = Message(link=session.link,
                      protocol="CAPFILE",
                      message_type="CapFileV6",
                      message_name="T_CapFileV6Tx")

        ms_addr_group = self.get_end_user_address(session.alias)

        msg['acHostOffice'] = pdn_link
        msg['acFileName'] = self.get_pcap_file_name(filename)
        msg['acFileForWardNetAddr'] = file_pdn_addr
        msg['acUserIpv6Addr'] = ms_addr_group[1]
        msg['wSendTimeInt'] = packet_interval
        return msg

    def send_capfile_v6capfile(self, session, bear, pdn_link, filename, file_pdn_addr, bearip, packet_interval):
        msg0 = self._encode_gpdu_message(session, bear, bearip)
        msg1 = self._encode_v6capfile_message(session, pdn_link, filename, file_pdn_addr, packet_interval)
        session.ne.send_msg([msg0, msg1])

    def send_auto_media(self, msg_type, session_alias, bear_alias=None, profile_name='', src=None, opposite=None):
        logger.debug('user send auto media %s.' % msg_type)
        session = self.get_session(session_alias)
        bear = self.get_bear(session_alias, bear_alias)
        if src is not None:
            self.init_session_ne(session_alias, src, opposite)
        session.msg_sequence_number = session.ne.generate_sequence_number()
        session.ne.add_user(self.user)

        self._send_auto_media(msg_type, profile_name, session, bear)

    def _send_auto_media(self, msg_type, profile_name, session, bear):
        msg_module = session.ne.msg_modules.get(msg_type)
        msg = Message(link=session.link,
                      protocol="AutoMedia",
                      message_type=msg_type,
                      module=msg_module)

        msg.parameters['acProfileName'] = profile_name

        self.fill_msg_by_module(msg.parameters, msg_type, msg_module.get("user"))
        session.fill_msg_by_module(msg.parameters, msg_type, msg_module.get("session"))
        bear.fill_msg_by_module(msg.parameters, msg_type, msg_module.get("bear"))
        session.ne.send_msg(msg)

    def send_traffic_ex(self, msg_type, session_alias, bear_alias, pdn_alias, bearip, src, opposite, data_length=64):
        session = self.get_session(session_alias)
        bear = self.get_bear(session_alias, bear_alias)

        if src is not None:
            self.init_session_ne(session_alias, src, opposite)
        msg0 = self._encode_gpdu_message(session, bear, bearip)

        pdn = NeRepository().find(pdn_alias)
        if pdn is None and msg_type != 'error_indication':
            raise Exception("pdn find fail, pdn_alias:{0}".format(pdn_alias))

        mtu = self.get_mtu(session.alias)
        eua = self.get_end_user_address(session_alias)
        if msg_type in ['UDPV4Tx', 'TCPV4Tx', 'ICMPRepV4Tx', 'ICMPReqV4Tx']:
            header_ip = {'acIpDstAddr': pdn.ip, 'acIpSrcAddr': eua[0]}
            if mtu is not None:
                header_ip.update({'dwMTU': mtu})
            last_ip = self.get_field_in_bear(session_alias, bear_alias, 'tCommHeader_IP')
            if last_ip is not None:
                DictUtility.update_dict(header_ip, last_ip)

            self.set_field_in_bear(session_alias, bear_alias, 'tCommHeader_IP', header_ip, serial_number=1)
        elif msg_type in ['UDPV6Tx', 'TCPV6Tx', 'ICMPRepV6Tx', 'ICMPReqV6Tx']:
            header_ipv6 = {'acIpv6Dst': pdn.ipv6, 'acIpv6Src': eua[1]}
            if mtu is not None:
                header_ipv6.update({'dwMTU': mtu})

            last_ipv6 = self.get_field_in_bear(session_alias, bear_alias, 'tCommHeader_IPv6')
            if last_ipv6 is not None:
                DictUtility.update_dict(header_ipv6, last_ipv6)

            self.set_field_in_bear(session_alias, bear_alias, 'tCommHeader_IPv6', header_ipv6, serial_number=1)
        else:
            Exception("not support msg:{0}".format(msg_type))

        self.set_field_in_bear(session_alias, bear_alias, 'tCommHeader_PktData', {'dwPacketLength': data_length})

        msg_module = session.ne.msg_modules.get(msg_type)
        msg1 = Message(link=session.link,
                       protocol='DATA',
                       message_type=msg_type,
                       module=msg_module)
        self.fill_msg_by_module(msg1.parameters, msg_type, msg_module.get("user"))
        session.fill_msg_by_module(msg1.parameters, msg_type, msg_module.get("session"))
        bear.fill_msg_by_module(msg1.parameters, msg_type, msg_module.get("bear"))
        session.ne.send_msg([msg0, msg1])

    def receive_traffic_ex(self, msg_type, session_alias, bear_alias, wait_time=10, check_sequence=True, expect=True):
        session = self.get_session(session_alias)
        bear = self.get_bear(session_alias, bear_alias)
        # layer0
        self._recv_gpdu_message(session, bear, wait_time, expect)

        msg = self.wait_message(msg_type, None, check_sequence, wait_time, expect)
        if not expect:
            return
        bear.check_expect(msg)

