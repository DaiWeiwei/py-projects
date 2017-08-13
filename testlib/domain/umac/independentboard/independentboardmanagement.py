# coding=utf-8
import re
import os
import time
from robot.api import logger
#from testlib.domain.umac.independentboard.IndependentBoardRepository import IndependentBoardRepository
from testlib.infrastructure.device.umac.independentboard import IndependentBoard
from testlib.infrastructure.device.umac.umacthread import UmacThread


class IndependentBoardManagement(object):
    #board_thread_duts = {}
    board_thread_dut_list = []

    @staticmethod
    def get_ind_board_info(umac_dut):
        ind_board_list = []
        cmd = 'SHOW INDBOARD;'
        cmd_result = umac_dut.execute_command(cmd)
        #temp = 'ACK SHOW INDBOARD:INFO="119"-"3"-"1"-"2"-"129.6.25.153"-"1"-"1"-"161"-"platform"-"platform"-"800"-"1",SYS_RESULT="0",SYS_LASTPACK="1"'
        result = re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"', cmd_result.return_string)
        #result = re.findall('[=&]"(\d+)"-"(\d+)"-"(\d+)"-"(\d+)"', temp)
        if not result:
            raise Exception("cannot get ind board info!")
        for ind_board_info in result:
            logger.info(
                "ind board info:ID={0},Board Type={1},Rack No={2},Shelf No".format(ind_board_info[0],
                                                                                   ind_board_info[1],
                                                                                   ind_board_info[2],
                                                                                   ind_board_info[3]))
            ind_board = IndependentBoard(ind_board_info[0], ind_board_info[1], ind_board_info[2], ind_board_info[3])
            #IndependentBoardRepository().add(ind_board_info[0], ind_board)
            ind_board_list.append(ind_board)
        return ind_board_list
    @staticmethod
    def get_independent_board_new_version_files(src_path):
        filename_list = []
        for parent, dirnames, filenames in os.walk(src_path):
            # print 'parent:',parent
            # print 'dirnames:',dirnames
            # print 'filenames:',filenames
            for filename in filenames:
                filename_list.append(os.path.join(parent, filename))
        return [filename for filename in filename_list if filename.lower().endswith('.pkg')]

    @staticmethod
    def get_ind_boards_be_upgraded(ind_board_list, umac_dut, src_path):
        src_filename_list = IndependentBoardManagement.get_independent_board_new_version_files(src_path)
        logger.info("ind version path:{0}".format(src_path))
        logger.info("ind verion files:{0}".format(src_filename_list))

        upgrade_ind_boards = []
        for board in ind_board_list:
            file_names = IndependentBoardManagement.get_current_ind_board_version_files(umac_dut, board)
            if not file_names:
                raise Exception(
                    "cannot get version file names of board id = {0}, address1 = {1}, address2 = {2}".format(board.id,
                                                                                                             board.address_1,
                                                                                                             board.address_2))
            same_file_list = IndependentBoardManagement.get_same_files_from_file_list1_in_file_list_2(file_names,
                                                                                                      src_filename_list)
            if same_file_list:
                logger.info(
                    "find same version files {0} in local , so not upgrade this board {1}".format(same_file_list,
                                                                                                  board.id))
            else:
                version_files = IndependentBoardManagement.get_files_by_regex(board.reg_file_name_of_match_src, src_filename_list)
                if not version_files:
                    raise Exception(
                        "cannot get src version files like {0}, board id = {1}".format(board.reg_file_name_of_match_src, board.id))

                board.version_file_name = version_files[0]
                logger.info("to be upload version file:{0}".format(board.simple_version_file_name))
                upgrade_ind_boards.append(board)

        return upgrade_ind_boards

    @staticmethod
    def delete_all_useless_versions_of_remote(umac_dut, board_list):
        logger.info("start delete all useless version of remote...")
        for board in board_list:
            IndependentBoardManagement._delete_remote_useless_version(umac_dut, board)

    @staticmethod
    def _classify_ind_boards(board_list):
        board_dict = {}
        for ind_board in board_list:
            if ind_board.board_type in board_dict:
                board_dict[ind_board.board_type].append(ind_board)
            else:
                board_dict[ind_board.board_type] = [ind_board]
        return board_dict

    @staticmethod
    def release_resource():
        IndependentBoardManagement.release_thread_umac_dut()

    @staticmethod
    def release_thread_umac_dut():
        for thread_umac_dut in IndependentBoardManagement.board_thread_dut_list:
            thread_umac_dut.close()
        IndependentBoardManagement.board_thread_dut_list = []

    @staticmethod
    def create_thread_umac_dut(umac_config, upgrade_boards):
        IndependentBoardManagement.board_thread_dut_list = []
        for idx,board in enumerate(upgrade_boards):
            logger.info('host={0},port={1},username={2},password={3},officeid={4},idx={5}'.format(umac_config.host,
                                                                                    umac_config.telnet_port,
                                                                                    umac_config.telnet_user_name,
                                                                                    umac_config.telnet_password,
                                                                                    umac_config.office_id,
                                                                                    str(idx)))
            thread_umac_dut = UmacThread(umac_config.host,
                                         umac_config.telnet_port,
                                         umac_config.telnet_user_name,
                                         umac_config.telnet_password,
                                         umac_config.office_id,
                                         str(100+idx))
            IndependentBoardManagement.board_thread_dut_list.append(thread_umac_dut)
        logger.info('create thread umac dut:{0}'.format(len(IndependentBoardManagement.board_thread_dut_list)))

    @staticmethod
    def load_ind_board_versions(umac_config, upgrade_ind_boards):
        #boards_dict = IndependentBoardManagement._classify_ind_boards(upgrade_ind_boards)
        #logger.info("boards_dict:{0}".format(str(boards_dict)))
        board_thread_dut_list = IndependentBoardManagement.board_thread_dut_list

##        board_cmds = {}
##        for board_type, ind_boards in boards_dict.items():
##            for ind_board in ind_boards:
##                if board_type in board_cmds:
##                    board_cmds[board_type].append(ind_board.get_cmd_of_add_ind_pkg())
##                else:
##                    board_cmds[board_type] = [ind_board.get_cmd_of_add_ind_pkg()]
        for idx,upgrade_ind in enumerate(upgrade_ind_boards):
            umac_thread = board_thread_dut_list[idx]
            logger.info("thread exe command:{0}".format(upgrade_ind.get_cmd_of_add_ind_pkg()))
            umac_thread.execute_command(upgrade_ind.get_cmd_of_add_ind_pkg())

        time.sleep(4*60)
        run_finish = False
        t = time.time()
        logger.info('start check load_ind_board_versions...')
        thread_dut_num = len(board_thread_dut_list)
        thread_dut_finish_num = 0
        while thread_dut_finish_num != thread_dut_num:
            thread_dut_finish_num = 0
            for umac_thread in board_thread_dut_list:
                if not umac_thread.is_run_finish():
                    logger.info("thread is running:{0}".format(umac_thread.flag))
                else:
                    logger.info("thread is over:{0}".format(umac_thread.flag))
                    thread_dut_finish_num += 1
            if thread_dut_finish_num != thread_dut_num:
                time.sleep(60)
        logger.info('check load_ind_board_versions finish,{0}s'.format(time.time() - t))

    @staticmethod
    def _delete_remote_useless_version(umac_dut, board):
        cmd = board.get_cmd_of_del_uneless_ind_pkg()
        logger.info(" cmd:{0}".format(cmd))
        cmd_result = umac_dut.execute_command(cmd)

    @staticmethod
    def get_board_version_serial_nos(umac_dut, board_list):
        for board in board_list:
            board.version_serial_no = IndependentBoardManagement._get_board_version_serial_no(umac_dut, board)
            logger.info("board:id = {0}, version file = {1}, serial no = {2}".format(board.id,
                                                                                     board.simple_version_file_name,
                                                                                     board.version_serial_no))

    @staticmethod
    def default_active_board_versions(umac_dut, board_list):
        for board in board_list:
            IndependentBoardManagement._default_active_board_version(umac_dut, board)

    @staticmethod
    def _default_active_board_version(umac_dut, board):
        cmd = board.get_cmd_of_default_active()
        logger.info("cmd:{0}".format(cmd))
        cmd_result = umac_dut.execute_command(cmd)

    @staticmethod
    def _get_board_version_serial_no(umac_dut, board):
        cmd = board.get_cmd_of_show_add_ind_pkg()
        logger.info(" cmd:{0}".format(cmd))
        cmd_result = umac_dut.execute_command(cmd,timeout=30,try_times=10,try_sleep=30)
        pattern = '"{0}"-".+?"-".+?"-".+?"-"(\d+?)"'.format(board.simple_version_file_name)
        serial_no_list = re.findall(pattern, cmd_result.return_string)
        if not serial_no_list:
            raise Exception('get serial no fail of {0}\ncmd result:{1}'.format(board.simple_version_file_name,
                                                                               cmd_result.return_string))
        return serial_no_list[0]

    @staticmethod
    def get_current_ind_board_version_files(umac_dut, ind_board):
        file_names = IndependentBoardManagement.get_current_ind_board_version_files_of_per_address(umac_dut,
                                                                                                   ind_board.id,
                                                                                                   ind_board.address_1)
        if not not file_names:
            return file_names
        ind_board.valid_address_1 = False
        return IndependentBoardManagement.get_current_ind_board_version_files_of_per_address(umac_dut,
                                                                                             ind_board.id,
                                                                                             ind_board.address_2)

    @staticmethod
    def get_current_ind_board_version_files_of_per_address(umac_dut, board_id, board_address):
        try:
            cmd = 'SHOW INDRUNSW:ID={0},ADDR={1};'.format(board_id, board_address)
            cmd_result = umac_dut.execute_command(cmd)
            return re.findall('([^\"]*\.pkg)\"', cmd_result.return_string)
        except:
            return None

    @staticmethod
    def get_omm_board_data(umac_dut):
        # Rack No.	Shelf No.	Left Slot No.	Right Slot No.	Server Type
        # server type = 2,表示是omm service，否则不是
        cmd = 'SHOW BKSVR;'
        pattern = '[=&]"(\d+)"-"(\d+)"-"\d+"-"\d+"-"(\d+)"'
        cmd_result = umac_dut.execute_command(cmd)
        result = re.findall(pattern, cmd_result.return_string)
        return IndependentBoardManagement._classify_omm_board_data(result)

    @staticmethod
    def valid_boards(umac_dut, upgrade_boards, omm_boards_data):
        # 先生效非OMM所在框的ECMM，EGFS和EGBS,etc
        # 最后生效OMM所在框的ECMM，EGFS和EGBS,etc
        omm_board, not_omm_board = IndependentBoardManagement._sort_out_omm_board(upgrade_boards, omm_boards_data)
        if not_omm_board:
            logger.info("start valididate not omm boards:")
            IndependentBoardManagement.print_boards_info(not_omm_board)
            IndependentBoardManagement._valid_boards(umac_dut, not_omm_board)
            logger.info("end valididate not omm boards:")
        if omm_board:
            logger.info("start valididate omm boards:")
            IndependentBoardManagement.print_boards_info(omm_board)
            IndependentBoardManagement._valid_boards(umac_dut, omm_board)
            logger.info("end valididate omm boards")

    @staticmethod
    def print_boards_info(board_list):
        for board in board_list:
            logger.info("  board:{0}".format(board))

    @staticmethod
    def _valid_boards(umac_dut, board_list,timeout = 15 * 60):
        invalid_boards = []
        if not board_list:
            raise Exception(" no board to be validated, please check it.")
        start_time = time.time()
        for board in board_list:
            logger.info(" valid board:cmd = {0}".format(board.get_cmd_of_aptenable_ind_pkg()))
            try:
                umac_dut.execute_command(board.get_cmd_of_aptenable_ind_pkg(), timeout=10)
            except:
                pass
            invalid_boards.append(board)
        time.sleep(5 * 60)
        while True:
            valid_boards = []
            if not invalid_boards:
                break
            for board in invalid_boards:
                if IndependentBoardManagement._check_board_validate(umac_dut, board):
                    valid_boards.append(board)
                time.sleep(2)
            for board in valid_boards:
                if board in invalid_boards:
                    invalid_boards.remove(board)

            if (time.time() - start_time) > timeout:
                break
            time.sleep(60)
        #如果没有遗留未生效的版本，则说明全部生效成功
        if not invalid_boards:
            return True
        else:
            logger.warn(" There are some invalid boards beyond timeout {0}s".format(timeout))
            IndependentBoardManagement.print_boards_info(invalid_boards)
            raise Exception("Validate boards fail!")

    @staticmethod
    def _check_board_validate(umac_dut, board):
        try:
            logger.info(" check valid board:id = {0}, cmd={1}".format(board.id, board.get_cmd_of_show_ind_run_sw()))
            cmd_result = umac_dut.execute_command(board.get_cmd_of_show_ind_run_sw(), 10)
            if not cmd_result:
                return False
            pattern = board.reg_file_name_of_validate
            version_file_names = re.findall(pattern, cmd_result.return_string)
            #如果返回的pkg文件只有一个，且是之前升级的文件名，那么说明版本已经生效
            if len(version_file_names) == 1 \
                and board.simple_version_file_name in version_file_names:
                logger.info(" board validated:id = {0}, version file = {1}".format(board.id, board.simple_version_file_name))
                return True
            elif version_file_names:
                logger.debug(" check validate board:id = {0}, return version files = {1}".format(board.id, version_file_names))
            else:
                logger.debug(" check validate board:id = {0}, result = {1}".format(board.id, cmd_result.return_string))
        except:
            return False

    @staticmethod
    def _sort_out_omm_board(upgrade_boards, omm_boards_data):
        omm_board = []
        not_omm_board = []
        for board in upgrade_boards:
            if board.rack_no_and_shelf_no in omm_boards_data:
                omm_board.append(board)
            else:
                not_omm_board.append(board)
        return omm_board, not_omm_board

    @staticmethod
    def _classify_omm_board_data(data):
        omm_board_data = []
        for board_data in data:
            # 表示是omm server
            if board_data[2] == '2':
                omm_board_data.append((board_data[0], board_data[1]))
        return omm_board_data

    @staticmethod
    def get_same_files_from_file_list1_in_file_list_2(file_list1, file_list2):
        file_names = []
        for file_name1 in file_list1:
            if [file_name_2 for file_name_2 in file_list2 if file_name_2.find(file_name1) >= 0]:
                file_names.append(file_name1)
        return file_names

    @staticmethod
    def get_files_by_regex(pattern, file_list):
        files = []
        if not pattern:
            return None
        for file_name in file_list:
            if re.search(pattern, file_name):
                files.append(file_name)
        return files

    @staticmethod
    def get_full_file_name(file_name, full_file_name_list):
        temp_list = [file_name_2 for file_name_2 in file_list2 if file_name_2.find(file_name) >= 0]
        if not not temp_list:
            return temp_list[0]
        return ''


if __name__ == '__main__':
    file_list1 = ["aa.pkg", "a.pkg"]
    file_list2 = ["c:/cc/a.pkg", "c:/dd/c.pkg"]
    #print IndependentBoardManagement.check_file_list1_in_file_list_2(file_list1, file_list2)
