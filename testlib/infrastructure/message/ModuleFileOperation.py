# coding=utf-8
import glob
import os

from testlib.infrastructure.message.MessageModule import MessageModule

class ModuleFileOperation(object):
    def load_ne_type(self):
        ne_types = []
        pat = '{0}/modulefile/*.yml'.format(os.path.abspath(os.path.dirname(__file__)))
        for filename in glob.glob(pat):
            basename = os.path.basename(filename)
            ne_types.append(basename[0:basename.rfind('.')].lower())
        return ne_types

    def get_ne_modules(self):
        ne_types = self.load_ne_type()
        for ne_type in ne_types:
            MessageModule().get(ne_type)
        return MessageModule().modules



