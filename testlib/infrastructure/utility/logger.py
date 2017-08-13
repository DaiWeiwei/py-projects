# coding=utf-8
import sys



class Log(object):
    @staticmethod
    def set_level(level='TRACE'):
        import logging

        logging.addLevelName(5, 'TRACE')
        logging.basicConfig(level=level,
                            format='%(asctime)s %(levelname)s : %(message)s',
                            datefmt="%Y%m%d %H:%M:%S",
                            stream=sys.stdout)
        logging.getLogger('RobotFramework')
