# coding=utf-8
from robot.api import logger

from testlib.domain.user.user_role.UserRole import UserRole
from testlib.infrastructure.message.Message import Message
from testlib.infrastructure.phonebook.phonebookoperate import PhoneBookOperate
from testlib.infrastructure.utility.CommDataArea import SERIAL_NUMBER_ALL
from testlib.infrastructure.utility.envpara.EnvPara import EnvPara
from testlib.infrastructure.message.InitModule import InitModule

class PsttUser(UserRole):
    def __init__(self, user):
        super(PsttUser, self).__init__(user)

    def encode_msg(self, msg_type, session, bear_alias):
        msg_module = session.ne.msg_modules.get(msg_type)
        msg = Message(link=session.link,
                      protocol="GTPV2",
                      message_type=msg_type,
                      module=msg_module)
        sequence_number = session.get_field("tGTPv2Head.dwSeqNum")
        if sequence_number:  # 如果用户通过关键字修改sequence_number,需要同步修改session的sequence_number
            session.set_sequence_number(sequence_number)

        msg["tGTPv2Head"] = {"dwSeqNum": session.msg_sequence_number, "dwTeid": self.get_field('Sgw_Teidc')}
        self.fill_msg_link_bear_info(session, msg)
        self.fill_msg_by_module(msg.parameters, msg_type, msg_module.get("user"))
        session.fill_msg_by_module(msg.parameters, msg_type, msg_module.get("session"))
        bear_module = msg_module.get("bear")
        if bear_module:
            rmv_bears = []
            mod_bears = []
            crt_bears = []
            for (i, bear) in session.bears.items():
                if "REMOVE" in bear_module and bear.need_remove:
                    rmv_bears.append(self._make_bear_ctx(msg, bear, "REMOVE", bear_module))
                elif "MODIFY" in bear_module and bear.need_modify:
                    mod_bears.append(self._make_bear_ctx(msg, bear, "MODIFY", bear_module))
                elif "CREATE" in bear_module and bear.need_create:
                    crt_bears.append(self._make_bear_ctx(msg, bear, "CREATE", bear_module))
                else:
                    continue
            if rmv_bears:
                msg[list(bear_module.get("REMOVE"))[0]] = rmv_bears
            if mod_bears:
                msg[list(bear_module.get("MODIFY"))[0]] = mod_bears
            if crt_bears:
                msg[list(bear_module.get("CREATE"))[0]] = crt_bears
        return msg

    
