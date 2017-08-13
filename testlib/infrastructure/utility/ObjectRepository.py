  # coding=utf-8
import logging


class ObjectRepository:

    def __init__(self):
        self._objDict = {}
        self._id_list = []
        self._objDictStack = []
        self._idListStack = []

    def _has_key(self, key):
        return key in self._objDict

    def add(self, key, obj):
        if self._has_key(key):
            raise Exception('key: "%s" is existed!' % (key,))
        self._objDict[key] = obj
        return True

    def find(self, key):
        obj = self._objDict.get(key)
        # if obj is None:
            # logging.info('find fail, key = %s not exist' % (key,))
        return obj

    def delete(self, key):
        if self._has_key(key):
            try:
                self._deallocate_id(self._objDict[key].id)
            except:
                pass
            del self._objDict[key]
            logging.debug('deleted ' + key)
            return True

        logging.warn('delete fail, key = %s not exist' % (key,))
        return False

    def clear(self):
        self._objDict.clear()
        self._id_list = []

    def allocate_id(self):
        try:
            i = self._id_list.index(0)
            self._id_list[i] = 1
            id_ = i + 1
        except:
            self._id_list.append(1)
            id_ = len(self._id_list)
        return id_

    def _deallocate_id(self, id_):
        self._id_list[id_ - 1] = 0

    def items(self):
        return self._objDict.items()

    def keys(self):
        return self._objDict.keys()

    def is_empty(self):
        return not self._objDict

    def stack_push(self):
        self._objDictStack.append(self._objDict)
        self._objDict = {}
        self._idListStack.append(self._id_list)
        self._id_list = []

    def stack_pop(self):
        if len(self._objDictStack) == 0:
            raise Exception('Object repository object stack crashed')
        self._objDict = self._objDictStack.pop()
        if len(self._idListStack) == 0:
            raise Exception('Object repository id_list stack crashed')
        self._id_list = self._idListStack.pop()
