# coding=utf-8
import os
from testlib.infrastructure.device.umac.boardtype import BoardType


class IndependentBoard(object):
    def __init__(self, id, board_type, rack_no, shelf_no):
        self._id = id
        self._board_type = board_type
        self._rack_no = rack_no  # 机架号
        self._shelf_no = shelf_no  # 机框号
        self._version_file_name = ''  # 版本文件名称(全路径)
        self._version_serial_no = ''  # 版本文件流水号
        # 匹配源文件的正则表达式
        self._reg_file_name_of_match_src = BoardType.get_file_name(board_type)
        # 匹配版本是否生效的正则表达式
        self._reg_file_name_of_validate = '"({0})"'.format(self._reg_file_name_of_match_src.replace('.+\.pkg', '[^"]+?\.pkg'))

        # 物理地址
        self._address_1 = "{0}-{1}-{2}-1".format(rack_no, shelf_no, BoardType.get_cpus(board_type)[0])
        self._address_2 = "{0}-{1}-{2}-1".format(rack_no, shelf_no, BoardType.get_cpus(board_type)[1])

        # 地址一是否有效，以是否能执行成功  SHOW INDRUNSW:ID=单板号,ADDR=物理地址; 为准
        self.valid_address_1 = True

    @property
    def id(self):
        return self._id

    @property
    def rack_no_and_shelf_no(self):
        return (self._rack_no, self._shelf_no)

    @property
    def board_type(self):
        return self._board_type

    @property
    def address_1(self):
        return self._address_1

    @property
    def address_2(self):
        return self._address_2

    @property
    def version_file_name(self):
        return self._version_file_name

    @property
    def version_serial_no(self):
        return self._version_serial_no

    @version_serial_no.setter
    def version_serial_no(self, value):
        self._version_serial_no = value

    @version_file_name.setter
    def version_file_name(self, value):
        self._version_file_name = value

    @property
    def simple_version_file_name(self):
        return os.path.split(self.version_file_name)[1]

    @property
    def reg_file_name_of_match_src(self):
        return self._reg_file_name_of_match_src

    @property
    def reg_file_name_of_validate(self):
        return self._reg_file_name_of_validate

    def __str__(self):
        return 'id = {0},' \
               'board type = {1},' \
               'rack no = {2},' \
               'shelf no = {3}'.format(self.id, self.board_type, self._rack_no, self._shelf_no)

    def get_cmd_of_show_ind_run_sw(self):
        if self.valid_address_1:
            return 'SHOW INDRUNSW:ID={0},ADDR={1};'.format(self.id, self.address_1)
        else:
            return 'SHOW INDRUNSW:ID={0},ADDR={1};'.format(self.id, self.address_2)

    def get_cmd_of_add_ind_pkg(self):
        if not self.simple_version_file_name:
            raise Exception("version file name is empty of id = {0} ,like {1}".format(self.id, self.reg_file_name))
        return 'ADD INDPKG:ID={0},PKGNAME="{1}";'.format(self.id, self.simple_version_file_name)

    def get_cmd_of_show_add_ind_pkg(self):
        return 'SHOW ADDINDPKG:ID={0};'.format(self.id)

    def get_cmd_of_del_uneless_ind_pkg(self):
        return 'DEL USELESS INDPKG:ID={0};'.format(self.id)

    def get_cmd_of_default_active(self):
        if not self.version_serial_no:
            raise Exception('serial no is empty of board id = {0}'.format(self.id))
        return 'DFTACT INDPKG:ID={0},PKGNAME="{1}",PKGVER={2};'.format(self.id,
                                                                       self.simple_version_file_name,
                                                                       self.version_serial_no)

    def get_cmd_of_aptenable_ind_pkg(self):
        return 'APTENABLE INDPKG:ID={0},LOC={1}&{2};'.format(self.id, self.address_1, self.address_2)
