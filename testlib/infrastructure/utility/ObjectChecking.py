from testlib.infrastructure.utility.Singleton import Singleton

@Singleton
class ObjectChecking(object):

    def is_valid_ailas(self,alias):
        return isinstance(alias,basestring) and len(alias.replace(' ','')) > 0
