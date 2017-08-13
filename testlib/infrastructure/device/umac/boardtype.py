class BoardType(object):
    board_types = {"0": ["ECMM_83XX_.+\.pkg", [29, 30]],
                   "3": ["EGBS_83XX_.+\.pkg", [19, 20]],
                   "4": ["EGFS_83XX_.+\.pkg", [21, 22]],
                   "14": ["EGBS_2_P.+\.pkg", [19, 20]],
                   "15": ["EXFS_P.+\.pkg", [21, 22]]
                   }

    @classmethod
    def get_file_name(cls, board_type):
        if board_type in cls.board_types:
            return cls.board_types[board_type][0]
        raise Exception("cannot get file name by value {0}".format(board_type))

    @classmethod
    def get_cpus(cls, board_type):
        if board_type in cls.board_types:
            return cls.board_types[board_type][1]
        raise Exception("cannot get cpus by value {0}".format(board_type))


if __name__ == '__main__':
    print BoardType.get_file_name("3")
    print BoardType.get_cpus("3")
