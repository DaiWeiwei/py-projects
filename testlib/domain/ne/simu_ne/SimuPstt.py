# coding=utf-8
import json
from testlib.domain.ne.Ne import Ne
# from testlib.infrastructure.utility import ThreadLogger
from robot.api import logger
from testlib.infrastructure.message.MessageBuffer import MessageBuffer

# from testlib.infrastructure.message.Message import Message
# from robot.api import logger

# RF->PSTT
EVENT_ID_OF_SEND_CONFIG_TO_PSTT = 0
EVENT_ID_OF_FILTER_PSTT_PROJECT_BY_DIR_NAMES = 1
EVENT_ID_OF_RUN_PSTT = 2
EVENT_ID_OF_CLOSE_PSTT = 3
EVENT_ID_OF_FILTER_BY_APN_SWITCH = 4
EVENT_ID_OF_CLASSIFY_BY_APN_CONFIG = 5
EVENT_ID_OF_SET_SIGTRACE = 6
EVENT_ID_OF_FILTER_BY_CONFIG_CMD_FOR_UMAC = 7
# PSTT->RF
EVENT_ID_OF_RETURN_SEND_CONFIG_TO_PSTT = 0
EVENT_ID_OF_RETURN_FILTER_PSTT_PROJECT_BY_DIR_NAMES = 1
EVENT_ID_OF_RETURN_RUN_PSTT = 2
EVENT_ID_OF_RETURN_CLOSE_PSTT = 3
EVENT_ID_OF_RETURN_FILTER_BY_APN_SWITCH = 4
EVENT_ID_OF_RETURN_CLASSIFY_BY_APN_CONFIG = 5
EVENT_ID_OF_RETURN_SET_SIGTRACE = 6
EVENT_ID_OF_RETURN_FILTER_BY_CONFIG_CMD_FOR_UMAC = 7

# MSG_NAME_OF_SEND_CONFIG_TO_PSTT = "send_config_to_pstt"
# MSG_NAME_OF_FILTER_PSTT_PROJECT_BY_DIR_NAMES = "filter_pstt_project_by_dir_names"
# MSG_NAME_OF_START_PSTT = 'start_pstt'
# MSG_NAME_OF_CLOSE_PSTT = 'close_pstt'
#
MSG_TYPE = "Project Version Valid Msg"

ENGINE_PROXY_FINISH = 2
PSTT_FINISH_WITH_FAIL_CASES = 3

WAIT_INFINIT_TIME = 1000000000


class SimuPstt(Ne):
    def __init__(self, ne_id, ip, ne_type):
        super(SimuPstt, self).__init__(ne_id, ip, ne_type)
        self._engine = None
        self._messages = MessageBuffer()
        self._run_index = 0
        self._set_not_update_fore_version_when_case_fail = False
        self._result = 0
        self._fore_version_upgrade = False  # 前台是否开始升级
        self.match_no_mml_case = 0 
        self.run_mml = 0 

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @engine.setter
    def set_not_update_fore_version_when_case_fail(self, value):
        self._set_not_update_fore_version_when_case_fail = value

    def send_msg(self, msg):
        logger.info('send to engine:{0}'.format(msg))
        self._engine.send_msg(msg)

    def receive_message(self, event_id, wait_time=10):
        condition = {"event_id": event_id}
        return self._messages.wait_message("", condition, False, wait_time, True)
        # if not expect:
        #     return
        # if msg.module is not None:
        #     self.check_expect(msg)
        #     # Message.check_expect(msg.parameters, self.get_expect_fields(msg.type), msg.type)
        #     self.save_field_from_msg(msg, module=msg.module.get('bear'))
        # self.save_ne_field_from_msg(msg)

    def append_receive_message(self, msg):
        self._messages.add_message([msg])

    def send_config_to_pstt(self, config={}):
        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_SEND_CONFIG_TO_PSTT,
            "config": config
        }
        self.send_msg(msg)

    def send_filter_pstt_project_by_apn_config(self, apn_file, soft_para_file):
        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_FILTER_BY_APN_SWITCH,
            "apn_file": apn_file,
            "soft_para_file": soft_para_file,
            "match_no_mml_case": self.match_no_mml_case
        }
        self.send_msg(msg)
        msg = self.receive_message(EVENT_ID_OF_RETURN_FILTER_BY_APN_SWITCH, WAIT_INFINIT_TIME)
        if not msg['result']:
            raise Exception("result of filter by apn switch is no suitable case")
        return msg['result']

    def send_classify_show_running_config_by_cases(self, apn_file, soft_para_file):
        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_CLASSIFY_BY_APN_CONFIG,
            "apn_file": apn_file,
            "soft_para_file": soft_para_file,
            "match_no_mml_case": self.match_no_mml_case
        }
        self.send_msg(msg)
        ret_msg = self.receive_message(EVENT_ID_OF_RETURN_CLASSIFY_BY_APN_CONFIG, WAIT_INFINIT_TIME)
        return ret_msg['result']

    def send_filter_by_config_cmd_for_umac(self, umac_config):
        local_path=umac_config.run_save_path
        config_cmd_file=local_path.replace("/", "\\")+'\\Batchcommandmml.txt'
        license_file = umac_config.license_path_0 +'\\analysis_license.txt'

        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_FILTER_BY_CONFIG_CMD_FOR_UMAC,
            "config_cmd_file": config_cmd_file,
            "license_file":license_file,
            "match_no_mml_case": self.match_no_mml_case,
            "net_type":umac_config.ne_type,
            "sgsnupgrade":umac_config.can_sgsn_upgrade(),
            "mmeupgrade":umac_config.can_mme_upgrade(),
        }
        self.send_msg(msg)
        ret_msg = self.receive_message(EVENT_ID_OF_RETURN_FILTER_BY_CONFIG_CMD_FOR_UMAC, WAIT_INFINIT_TIME)
        return ret_msg['result']

    def send_sigtrace_flag(self, flag):
        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_SET_SIGTRACE,
            "sigtrace_flag": int(flag)
        }
        self.send_msg(msg)

    # def inc_run_index(self):
    #     self._run_index = (self._run_index + 1)
    #     if self._run_index > 2:
    #         self._run_index = 1

    def send_run_pstt(self, upgrade,select_last_run_cases):
        # self.inc_run_index()
        self._fore_version_upgrade = upgrade
        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_RUN_PSTT,
            "upgrade": self._fore_version_upgrade,
            "select_last_run_cases": select_last_run_cases,
            "run_mml": self.run_mml
        }
        self.send_msg(msg)

        ret_msg = self.receive_message(EVENT_ID_OF_RETURN_RUN_PSTT, WAIT_INFINIT_TIME)
        self._result = ret_msg["result"]
        # if msg["result"] == PSTT_FINISH_WITH_FAIL_CASES and :
        #    raise Exception("pstt run fail! please check the fail case first!")

        return self._result

    def is_run_with_all_success(self):
        return self._result is ENGINE_PROXY_FINISH

    def send_close_pstt(self):
        msg = {
            "id": self.id,
            "type": MSG_TYPE,
            "event_id": EVENT_ID_OF_CLOSE_PSTT
        }
        self.send_msg(msg)


if __name__ == '__main__':
    sn = SimuPstt("pstt", "10.42.188.33", "pstt")
    sn.send_config_to_pstt({"procedure_path": "d:"})
